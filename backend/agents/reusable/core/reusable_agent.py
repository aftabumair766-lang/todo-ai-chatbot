"""
Reusable Agent Core
===================

Domain-agnostic AI agent that works with any DomainAdapter.

This is the core reusable agent that can be configured for:
- Todo Management (TodoDomainAdapter)
- CRM Systems (CRMDomainAdapter)
- E-commerce (EcommerceDomainAdapter)
- Support Chatbots (SupportDomainAdapter)
- Any other domain via custom adapters

Architecture:
    - Stateless (no in-memory state)
    - MCP-First (all operations via MCP tools)
    - OpenAI Function Calling for tool orchestration
    - Domain adapter pattern for customization

Usage:
    from backend.agents.reusable.core.reusable_agent import ReusableAgent
    from backend.agents.reusable.adapters.todo_adapter import TodoDomainAdapter

    # Create agent with domain adapter
    agent = ReusableAgent(adapter=TodoDomainAdapter())

    # Process messages
    result = await agent.process_message(
        user_id="user123",
        message="Add a task to buy milk",
        conversation_history=[],
        db=db_session
    )

    print(result["response"])  # Agent's reply
    print(result["tool_calls"])  # Tools invoked
"""

from typing import Any, Dict, List, Optional
import logging
import json
from openai import AsyncOpenAI
from backend.config import get_settings
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)
settings = get_settings()


class ReusableAgent:
    """
    Domain-agnostic AI agent powered by OpenAI and configured by DomainAdapter.

    This agent is reusable across ANY domain by swapping the adapter.
    """

    def __init__(
        self,
        adapter: DomainAdapter,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize reusable agent with domain adapter.

        Args:
            adapter: Domain-specific configuration (TodoDomainAdapter, CRMDomainAdapter, etc.)
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
            model: OpenAI model name (defaults to adapter.get_model_name())
        """
        self.adapter = adapter
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or adapter.get_model_name()
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Load tools and handlers from adapter
        self.tools = adapter.get_tools()
        self.tool_handlers = adapter.get_tool_handlers()
        self.system_prompt = adapter.get_system_prompt()

        logger.info(f"ReusableAgent initialized with {len(self.tools)} tools from {adapter.__class__.__name__}")

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: List[Dict[str, str]],
        db
    ) -> Dict[str, Any]:
        """
        Process user message using domain adapter configuration.

        Args:
            user_id: Authenticated user ID
            message: User's latest message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            db: Database session (injected, stateless)

        Returns:
            {
                "response": str,  # Agent's response text
                "tool_calls": List[Dict],  # Tools invoked (for transparency)
            }

        Constitution Compliance:
            - Stateless: No in-memory conversation storage
            - MCP-First: All operations via domain adapter's MCP tool wrappers
        """

        # Check for greeting (domain-specific)
        if self.adapter.is_greeting(message):
            greeting_response = self.adapter.get_greeting_response()
            if greeting_response:
                return {
                    "response": greeting_response,
                    "tool_calls": []
                }

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history (last 50 messages for token budget)
        messages.extend(conversation_history[-50:])

        # Add current user message
        messages.append({"role": "user", "content": message})

        try:
            # Call OpenAI API with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None
            )

            message_response = response.choices[0].message
            tool_calls_made = []

            # Handle tool calls
            if message_response.tool_calls:
                for tool_call in message_response.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Agent calling tool: {function_name} with args: {function_args}")

                    # Validate tool input (optional, domain-specific)
                    validation_error = self.adapter.validate_tool_input(function_name, function_args)
                    if validation_error:
                        result = {
                            "error": True,
                            "message": validation_error
                        }
                    else:
                        # Invoke tool handler from adapter
                        result = await self._execute_tool(
                            function_name,
                            function_args,
                            user_id,
                            db
                        )

                    tool_calls_made.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "result": result
                    })

                    # Add tool result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                # Get final response after tool execution
                second_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                final_response_text = second_response.choices[0].message.content
            else:
                # No tool calls, use direct response
                final_response_text = message_response.content

            # Apply domain-specific formatting
            formatted_response = self.adapter.format_response(
                final_response_text,
                context={"tool_calls": tool_calls_made}
            )

            return {
                "response": formatted_response,
                "tool_calls": tool_calls_made
            }

        except Exception as e:
            logger.error(f"Error in ReusableAgent.process_message: {e}")
            error_message = self.adapter.handle_error(e, context={"message": message})
            return {
                "response": error_message,
                "tool_calls": []
            }

    async def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str,
        db
    ) -> Dict[str, Any]:
        """
        Execute tool handler from domain adapter.

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments from OpenAI
            user_id: User ID for context
            db: Database session

        Returns:
            Tool execution result
        """
        handler = self.tool_handlers.get(tool_name)

        if not handler:
            return {
                "error": True,
                "message": f"Unknown tool: {tool_name}"
            }

        try:
            # Inject user_id and db into arguments
            result = await handler(user_id=user_id, db=db, **arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "error": True,
                "message": f"Tool execution failed: {str(e)}"
            }

    def add_tool(self, tool_definition: Dict[str, Any], handler: callable):
        """
        Dynamically add a new tool (advanced usage).

        Args:
            tool_definition: OpenAI function calling tool definition
            handler: Async function to handle tool calls
        """
        self.tools.append(tool_definition)
        self.tool_handlers[tool_definition["function"]["name"]] = handler
        logger.info(f"Added tool: {tool_definition['function']['name']}")

    def remove_tool(self, tool_name: str):
        """
        Remove a tool from the agent.

        Args:
            tool_name: Name of the tool to remove
        """
        self.tools = [t for t in self.tools if t["function"]["name"] != tool_name]
        self.tool_handlers.pop(tool_name, None)
        logger.info(f"Removed tool: {tool_name}")
