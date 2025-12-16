"""
Generic AI Agent Base Class - Reusable Across ANY Project

This is a generic agent that works with any OpenAI function calling tools.
You can use this in e-commerce, calendar, support, or any domain.

Usage Example:
    from base_agent import BaseAgent

    # Define your tools
    tools = [...]  # OpenAI function calling format

    # Define tool handlers
    handlers = {
        "my_tool": my_tool_handler_function
    }

    # Create agent
    agent = BaseAgent(
        api_key="sk-...",
        tools=tools,
        tool_handlers=handlers,
        system_prompt="You are a helpful assistant"
    )

    # Use agent
    result = await agent.process_message(
        user_message="Help me",
        user_id="user_123",
        conversation_history=[],
        db=db_session
    )

Constitution Compliance:
- Principle I: MCP-First (tools via function calling)
- Principle II: Stateless (no instance state)
"""

from typing import Any, Dict, List, Optional, Callable
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Generic AI agent that works with any set of OpenAI function calling tools.

    This agent is completely domain-agnostic. You provide:
    1. Tools (OpenAI function calling format)
    2. Tool handlers (async functions that execute the tools)
    3. System prompt (defines agent personality/role)

    The agent handles:
    - OpenAI API integration
    - Tool execution orchestration
    - Conversation history management
    - Error handling

    Attributes:
        client: AsyncOpenAI client
        model: GPT model to use
        system_prompt: System message defining agent behavior
        tools: List of tool definitions (OpenAI format)
        tool_handlers: Dict mapping tool names to handler functions
        greeting_detector: Optional function to detect greetings
        greeting_response: Response to return for greetings
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        system_prompt: str = "You are a helpful AI assistant.",
        tools: Optional[List[Dict]] = None,
        tool_handlers: Optional[Dict[str, Callable]] = None,
        greeting_detector: Optional[Callable[[str], bool]] = None,
        greeting_response: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize generic agent.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4-turbo-preview)
            system_prompt: System message defining agent role
            tools: List of tool definitions in OpenAI format
            tool_handlers: Dict of {tool_name: handler_function}
            greeting_detector: Optional function to detect greetings
            greeting_response: Response for greetings
            temperature: Model temperature (0-2)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        self.greeting_detector = greeting_detector
        self.greeting_response = greeting_response
        self.temperature = temperature

        logger.info(
            f"BaseAgent initialized: model={model}, tools={len(self.tools)}"
        )

    async def process_message(
        self,
        user_message: str,
        user_id: str,
        conversation_history: List[Dict[str, str]],
        db: Any = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Process user message with OpenAI and execute tools.

        Args:
            user_message: User's message
            user_id: User identifier (passed to tool handlers)
            conversation_history: Previous messages [{"role": "...", "content": "..."}]
            db: Optional database session (passed to tool handlers)
            **kwargs: Additional arguments passed to tool handlers

        Returns:
            {
                "response": str,  # Agent's text response
                "tool_calls": List[Dict],  # Tools that were executed
            }
        """
        # Step 1: Check for greeting (if detector provided)
        if self.greeting_detector and self.greeting_detector(user_message):
            logger.info(f"Greeting detected for user {user_id}")
            return {
                "response": self.greeting_response or "Hello! How can I help?",
                "tool_calls": [],
            }

        # Step 2: Build messages array
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history (limit to last 50 for token budget)
        messages.extend(conversation_history[-50:])

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Step 3: Call OpenAI API
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=self.temperature,
            )

            message_response = response.choices[0].message
            tool_calls_made = []

            # Step 4: Handle tool calls
            if message_response.tool_calls:
                for tool_call in message_response.tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)

                    logger.info(
                        f"Tool call: {function_name} with args: {function_args}"
                    )

                    # Execute tool handler if registered
                    if function_name in self.tool_handlers:
                        handler = self.tool_handlers[function_name]

                        try:
                            # Call handler with user_id, db, and function args
                            result = await handler(
                                user_id=user_id, db=db, **function_args, **kwargs
                            )

                            tool_calls_made.append(
                                {
                                    "tool": function_name,
                                    "arguments": function_args,
                                    "result": result,
                                }
                            )

                            # Add to conversation for next turn
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [tool_call],
                                }
                            )
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": str(result),
                                }
                            )

                        except Exception as e:
                            logger.error(
                                f"Tool handler error: {function_name}, {str(e)}"
                            )
                            tool_calls_made.append(
                                {
                                    "tool": function_name,
                                    "arguments": function_args,
                                    "error": str(e),
                                }
                            )

                            # Add error to conversation
                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [tool_call],
                                }
                            )
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": f"Error: {str(e)}",
                                }
                            )
                    else:
                        logger.warning(
                            f"No handler registered for tool: {function_name}"
                        )
                        tool_calls_made.append(
                            {
                                "tool": function_name,
                                "arguments": function_args,
                                "error": "No handler registered",
                            }
                        )

                # Step 5: Get final response after tool execution
                second_response = await self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=self.temperature
                )
                final_response_text = second_response.choices[0].message.content

            else:
                # No tool calls, use direct response
                final_response_text = message_response.content

            logger.info(
                f"Agent response generated: {len(tool_calls_made)} tools executed"
            )

            return {
                "response": final_response_text or "I'm not sure how to help with that.",
                "tool_calls": tool_calls_made,
            }

        except Exception as e:
            logger.error(f"Agent processing error: {str(e)}", exc_info=True)
            return {
                "response": f"⚠️ I encountered an error: {str(e)}. Please try again.",
                "tool_calls": [],
            }

    def add_tool(self, tool_definition: Dict, handler: Callable) -> None:
        """
        Dynamically add a tool to the agent.

        Args:
            tool_definition: Tool definition in OpenAI format
            handler: Async function to handle tool execution
        """
        self.tools.append(tool_definition)
        tool_name = tool_definition["function"]["name"]
        self.tool_handlers[tool_name] = handler
        logger.info(f"Tool added: {tool_name}")

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the agent.

        Args:
            tool_name: Name of tool to remove
        """
        self.tools = [
            t for t in self.tools if t["function"]["name"] != tool_name
        ]
        if tool_name in self.tool_handlers:
            del self.tool_handlers[tool_name]
        logger.info(f"Tool removed: {tool_name}")

    def get_tool_names(self) -> List[str]:
        """Get list of registered tool names."""
        return [tool["function"]["name"] for tool in self.tools]
