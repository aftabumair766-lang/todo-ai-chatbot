# Agent Reusability Guide

This document explains how to use the Todo Agent as a **reusable component** in other projects.

## 🎯 Agent Architecture Overview

### What Makes This Agent Reusable?

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR PROJECT                         │
│  ┌───────────────────────────────────────────────┐     │
│  │         Todo Agent (Reusable Core)            │     │
│  │  ┌─────────────────────────────────────────┐  │     │
│  │  │  1. OpenAI Client (Generic)             │  │     │
│  │  │  2. Greeting Detection (Customizable)   │  │     │
│  │  │  3. Tool Execution Engine (Generic)     │  │     │
│  │  │  4. Response Formatting (Customizable)  │  │     │
│  │  └─────────────────────────────────────────┘  │     │
│  └───────────────────────────────────────────────┘     │
│                         ↓                               │
│  ┌───────────────────────────────────────────────┐     │
│  │         Your Custom Tools (Pluggable)         │     │
│  │  - add_task, list_tasks, etc. (Todo)          │     │
│  │  - create_order, ship_order (E-commerce)      │     │
│  │  - book_appointment, cancel (Calendar)        │     │
│  │  - ANY domain-specific functions!            │     │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Key Reusable Components:

1. **`run_todo_agent()`** - Main agent runner (generic)
2. **`is_greeting()`** - Greeting detection (customizable)
3. **Tool wrapper pattern** - MCP tool integration (pluggable)
4. **OpenAI integration** - GPT-4 function calling (generic)

---

## 📦 Method 1: Package as Python Module

### Option A: Local Package (Same Machine)

Create a standalone Python package:

```bash
# 1. Create package structure
mkdir -p ~/my-agents/todo_agent
cp -r backend/agents/* ~/my-agents/todo_agent/

# 2. Create setup.py
cat > ~/my-agents/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="todo-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
    ],
    author="Your Name",
    description="Reusable AI agent for natural language task management",
)
EOF

# 3. Install in other projects
pip install -e ~/my-agents/
```

### Option B: Git Repository (Share Across Projects)

```bash
# 1. Create dedicated repo
cd ~/my-agents
git init
git add .
git commit -m "Initial commit: Reusable Todo Agent"

# 2. Push to GitHub/GitLab
git remote add origin https://github.com/yourusername/todo-agent.git
git push -u origin main

# 3. Install in other projects
pip install git+https://github.com/yourusername/todo-agent.git
```

### Option C: PyPI Package (Public Distribution)

```bash
# 1. Build package
python setup.py sdist bdist_wheel

# 2. Upload to PyPI
pip install twine
twine upload dist/*

# 3. Install anywhere
pip install todo-agent
```

---

## 🔧 Method 2: Copy Agent Files Directly

### Quick Start (5 minutes):

```bash
# In your new project
mkdir -p new_project/agents
cp todo-chatbot/backend/agents/* new_project/agents/

# Update imports in your new project
# Change: from backend.agents.todo_agent import run_todo_agent
# To: from agents.todo_agent import run_todo_agent
```

---

## 🎨 Method 3: Generic Agent Base Class

### Create a Generic Agent (Recommended for Multiple Projects)

Create `base_agent.py`:

```python
"""
Generic AI Agent Base Class
Reusable across ANY project with OpenAI function calling
"""

from typing import Any, Dict, List, Optional, Callable
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Generic AI agent that works with any set of tools.

    Usage:
        # Define your tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_order",
                    "description": "Create a new order",
                    "parameters": {...}
                }
            }
        ]

        # Create agent
        agent = BaseAgent(
            api_key="sk-...",
            model="gpt-4-turbo-preview",
            system_prompt="You are an e-commerce assistant",
            tools=tools,
            tool_handlers={
                "create_order": create_order_handler
            }
        )

        # Run agent
        result = await agent.process_message(
            user_message="I want to order a laptop",
            user_id="user_123",
            conversation_history=[],
            db=db_session
        )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        system_prompt: str = "You are a helpful AI assistant.",
        tools: Optional[List[Dict]] = None,
        tool_handlers: Optional[Dict[str, Callable]] = None,
        greeting_detector: Optional[Callable] = None,
        greeting_response: Optional[str] = None,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        self.greeting_detector = greeting_detector
        self.greeting_response = greeting_response

    async def process_message(
        self,
        user_message: str,
        user_id: str,
        conversation_history: List[Dict[str, str]],
        db: Any = None,
    ) -> Dict[str, Any]:
        """Process user message with OpenAI and execute tools."""

        # Check for greeting
        if self.greeting_detector and self.greeting_detector(user_message):
            return {
                "response": self.greeting_response or "Hello! How can I help?",
                "tool_calls": []
            }

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(conversation_history[-50:])
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
            )

            message_response = response.choices[0].message
            tool_calls_made = []

            # Handle tool calls
            if message_response.tool_calls:
                for tool_call in message_response.tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)

                    # Execute tool handler
                    if function_name in self.tool_handlers:
                        handler = self.tool_handlers[function_name]
                        result = await handler(
                            user_id=user_id,
                            db=db,
                            **function_args
                        )

                        tool_calls_made.append({
                            "tool": function_name,
                            "arguments": function_args,
                            "result": result
                        })

                        # Add to conversation
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result)
                        })

                # Get final response
                second_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                final_response_text = second_response.choices[0].message.content
            else:
                final_response_text = message_response.content

            return {
                "response": final_response_text,
                "tool_calls": tool_calls_made
            }

        except Exception as e:
            logger.error(f"Agent error: {e}")
            return {
                "response": f"⚠️ Error: {str(e)}",
                "tool_calls": []
            }
```

### Using the Generic Agent in Different Projects:

#### Example 1: E-Commerce Agent

```python
from base_agent import BaseAgent

# Define e-commerce tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create a new order",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["product_id", "quantity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Track order status",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    }
]

# Define tool handlers
async def create_order_handler(user_id, product_id, quantity, db):
    # Your e-commerce logic
    return {"success": True, "order_id": "ORD123"}

async def track_order_handler(user_id, order_id, db):
    # Your tracking logic
    return {"status": "shipped", "eta": "2 days"}

# Create agent
ecommerce_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt="You are an e-commerce assistant. Help users order products and track shipments.",
    tools=tools,
    tool_handlers={
        "create_order": create_order_handler,
        "track_order": track_order_handler,
    }
)

# Use it
result = await ecommerce_agent.process_message(
    user_message="I want to order product ABC123",
    user_id="user_456",
    conversation_history=[],
    db=db_session
)
```

#### Example 2: Calendar Agent

```python
from base_agent import BaseAgent

# Define calendar tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a calendar appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"}
                },
                "required": ["title", "date", "time"]
            }
        }
    }
]

async def book_appointment_handler(user_id, title, date, time, db):
    # Your calendar logic
    return {"success": True, "appointment_id": "APT789"}

calendar_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt="You are a calendar assistant. Help users manage appointments.",
    tools=tools,
    tool_handlers={"book_appointment": book_appointment_handler}
)
```

#### Example 3: Customer Support Agent

```python
from base_agent import BaseAgent

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Search knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]

async def create_ticket_handler(user_id, subject, priority="medium", db=None):
    return {"success": True, "ticket_id": "TKT456"}

async def search_kb_handler(user_id, query, db=None):
    return {"results": ["Article 1", "Article 2"]}

support_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt="You are a customer support assistant. Help users with their issues.",
    tools=tools,
    tool_handlers={
        "create_ticket": create_ticket_handler,
        "search_kb": search_kb_handler
    }
)
```

---

## 🔍 How to Find Reusable Agents

### 1. GitHub Search

```bash
# Search for OpenAI agent implementations
site:github.com "openai" "agent" "function calling" "tools"
site:github.com "mcp server" "tools" python
site:github.com "chatbot framework" "reusable"
```

**Popular Repos:**
- LangChain: https://github.com/langchain-ai/langchain
- AutoGPT: https://github.com/Significant-Gravitas/AutoGPT
- OpenAI Cookbook: https://github.com/openai/openai-cookbook

### 2. Python Package Index (PyPI)

```bash
pip search "openai agent"
pip search "chatbot framework"
pip search "function calling"
```

**Popular Packages:**
- `langchain` - Full agent framework
- `openai` - Official OpenAI SDK
- `semantic-kernel` - Microsoft's AI framework

### 3. Model Context Protocol (MCP) Registry

Check official MCP documentation:
- https://modelcontextprotocol.io/
- Look for MCP server implementations
- Browse community tools and agents

---

## 📋 Checklist for Reusable Agent Design

When creating a reusable agent, ensure:

- [ ] **Generic**: No hardcoded domain logic
- [ ] **Configurable**: System prompt, tools, model customizable
- [ ] **Pluggable**: Easy to add/remove tools
- [ ] **Stateless**: No global state, session-per-request
- [ ] **Well-documented**: Clear usage examples
- [ ] **Type hints**: Full Python type annotations
- [ ] **Error handling**: Graceful failures
- [ ] **Testing**: Unit tests included
- [ ] **Logging**: Structured logging for debugging
- [ ] **Dependencies**: Minimal, clearly listed

---

## 🚀 Quick Start: Use Todo Agent in New Project

```bash
# 1. Copy agent files
cp -r todo-chatbot/backend/agents new-project/

# 2. Install dependencies
pip install openai sqlalchemy pydantic

# 3. Use in your code
from agents.todo_agent import run_todo_agent

# 4. Define your custom tools (or reuse existing)
from your_app.tools import my_custom_tool

# 5. Run agent
result = await run_todo_agent(
    user_id="user_123",
    message="Do something",
    conversation_history=[],
    db=db_session
)
```

---

## 💡 Best Practices

1. **Separate Concerns**: Keep agent logic separate from business logic
2. **Configuration Files**: Use YAML/JSON for tool definitions
3. **Version Control**: Tag releases (v1.0.0, v1.1.0)
4. **Documentation**: README with examples
5. **Testing**: Mock OpenAI calls in tests
6. **Security**: Never hardcode API keys

---

## 📚 Next Steps

1. Extract agent to standalone repo
2. Add more generic features (streaming, vision, etc.)
3. Publish to PyPI for easy installation
4. Create agent marketplace/registry
5. Build CLI tool for agent testing

**Your agent is already 90% reusable!** 🎉
