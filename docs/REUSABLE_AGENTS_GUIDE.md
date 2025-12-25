# Building Reusable AI Agents: Complete Guide

## Executive Summary

This project has extracted a **domain-agnostic AI agent framework** from the Todo chatbot. The same agent architecture can now power:

- ✅ **Todo Management** (existing)
- ✅ **CRM Systems** (example included)
- 🚀 **E-commerce Platforms**
- 🚀 **Support Chatbots**
- 🚀 **Any domain you can imagine**

**Key Achievement:** Reduced 568 lines of domain-specific code to 10 lines by extracting reusable components.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Creating Domain Adapters](#creating-domain-adapters)
5. [Real Examples](#real-examples)
6. [Migration Guide](#migration-guide)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

---

## Quick Start

### Using the Todo Agent

```python
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

# Create agent
agent = ReusableAgent(adapter=TodoDomainAdapter())

# Use it
result = await agent.process_message(
    user_id="user123",
    message="Add buy milk to my list",
    conversation_history=[],
    db=db_session
)

print(result["response"])
# Output: "✅ Task added: Buy milk"
```

### Creating a Custom Agent

```python
from backend.agents.reusable import ReusableAgent, DomainAdapter

# Define your domain
class WeatherAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a weather assistant..."

    def get_tools(self):
        return [{"type": "function", "function": {...}}]

    def get_tool_handlers(self):
        return {"get_weather": self._get_weather}

    async def _get_weather(self, user_id, city, db=None):
        # Your weather logic
        return {"temperature": "20°C", "condition": "sunny"}

# Use it
weather_agent = ReusableAgent(adapter=WeatherAdapter())
```

---

## Architecture Overview

### The Problem (Before)

Original `todo_agent.py` had 568 lines with:
- Hard-coded system prompt
- Hard-coded tool definitions
- Hard-coded tool dispatch logic
- Tightly coupled to Todo domain

**Result:** Cannot reuse for CRM, e-commerce, or other domains.

### The Solution (After)

Extracted into 3 layers:

```
┌─────────────────────────────────────┐
│   ReusableAgent (Generic Core)     │  ← Works with ANY domain
│   - OpenAI API calls                │
│   - Tool routing                    │
│   - Conversation management         │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│   DomainAdapter (Configuration)     │  ← Domain-specific config
│   - System prompt                   │
│   - Tool definitions                │
│   - Tool handlers                   │
│   - Response formatting             │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│   MCP Tools (Data Operations)       │  ← Database/API calls
│   - CRUD operations                 │
│   - Business logic                  │
└─────────────────────────────────────┘
```

**Result:** Create new agents by writing ONLY the configuration (adapter).

---

## Core Components

### 1. ReusableAgent (`core/reusable_agent.py`)

Generic agent that works with any domain adapter.

**Responsibilities:**
- Call OpenAI API with configured tools
- Route tool calls to adapter handlers
- Manage conversation context
- Handle errors gracefully

**Key Methods:**
```python
class ReusableAgent:
    def __init__(self, adapter: DomainAdapter):
        # Load configuration from adapter
        self.tools = adapter.get_tools()
        self.tool_handlers = adapter.get_tool_handlers()
        self.system_prompt = adapter.get_system_prompt()

    async def process_message(self, user_id, message, conversation_history, db):
        # 1. Check for greetings (domain-specific)
        # 2. Build OpenAI messages
        # 3. Call OpenAI with tools
        # 4. Execute tools via adapter
        # 5. Format and return response
        pass

    def add_tool(self, tool_definition, handler):
        # Dynamically add tools at runtime
        pass

    def remove_tool(self, tool_name):
        # Remove tools
        pass
```

### 2. DomainAdapter (`adapters/base_adapter.py`)

Abstract base class defining the adapter interface.

**Required Methods:**
```python
class DomainAdapter(ABC):
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent personality and instructions"""
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict]:
        """Return OpenAI tool definitions"""
        pass

    @abstractmethod
    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Return tool name → handler function mapping"""
        pass
```

**Optional Overrides:**
```python
    def is_greeting(self, message: str) -> bool:
        """Detect greetings (domain-specific)"""
        pass

    def get_greeting_response(self) -> str:
        """Return greeting message"""
        pass

    def format_response(self, response: str, context: Dict) -> str:
        """Apply domain-specific formatting"""
        pass

    def validate_tool_input(self, tool_name: str, arguments: Dict) -> Optional[str]:
        """Validate tool arguments before execution"""
        pass

    def handle_error(self, error: Exception, context: Dict) -> str:
        """Generate user-friendly error messages"""
        pass

    def get_model_name(self) -> str:
        """Return preferred OpenAI model"""
        pass
```

### 3. Domain-Specific Adapters

Concrete implementations for each domain:

- **TodoDomainAdapter** (`adapters/todo_adapter.py`) - Task management
- **CRMDomainAdapter** (`adapters/crm_adapter.py`) - Customer relationships
- **YourAdapter** - Your custom domain!

---

## Creating Domain Adapters

### Step 1: Define Your Domain

Answer these questions:
1. **What is the domain?** (e.g., Weather, E-commerce, Support)
2. **What can users do?** (e.g., Check weather, Buy products, Create tickets)
3. **What personality?** (e.g., Friendly, Professional, Technical)
4. **What response style?** (e.g., Emojis, Formal, Concise)

### Step 2: Create Adapter Class

```python
# backend/agents/reusable/adapters/your_adapter.py

from backend.agents.reusable.adapters.base_adapter import DomainAdapter
from typing import Dict, List, Callable, Any

class YourDomainAdapter(DomainAdapter):
    """Your domain description"""

    def get_system_prompt(self) -> str:
        return """You are a [personality] assistant that helps with [domain].

**Capabilities:**
- [Capability 1]
- [Capability 2]

**Response Style:**
- [Style guideline 1]
- [Style guideline 2]

**Important:**
- [Critical instruction 1]
- [Critical instruction 2]
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "your_tool_name",
                    "description": "What the tool does",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {
                                "type": "string",
                                "description": "Parameter description"
                            }
                        },
                        "required": ["param1"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        return {
            "your_tool_name": self._your_tool_handler
        }

    async def _your_tool_handler(self, user_id: str, param1: str, db=None) -> Dict[str, Any]:
        """Tool implementation"""
        # Your business logic here
        return {
            "success": True,
            "message": "Operation completed"
        }
```

### Step 3: Use Your Adapter

```python
from backend.agents.reusable import ReusableAgent
from backend.agents.reusable.adapters.your_adapter import YourDomainAdapter

# Create agent
your_agent = ReusableAgent(adapter=YourDomainAdapter())

# Use it
result = await your_agent.process_message(
    user_id="user123",
    message="Natural language request",
    conversation_history=[],
    db=db_session
)
```

---

## Real Examples

### Example 1: Todo Management (Existing)

**Domain:** Task management with emojis

**Code:**
```python
# backend/agents/reusable/adapters/todo_adapter.py

class TodoDomainAdapter(DomainAdapter):
    def get_system_prompt(self):
        return """You are a friendly Todo Task Assistant...
        Use emojis: ✅ = completed, ⏳ = pending, 🗑️ = deleted"""

    def get_tools(self):
        return [
            {"type": "function", "function": {
                "name": "add_task",
                "description": "Add a new task",
                # ...
            }}
        ]

    def get_tool_handlers(self):
        return {
            "add_task": self._add_task_handler,
            "list_tasks": self._list_tasks_handler
        }

    async def _add_task_handler(self, user_id, title, description=None, db=None):
        from backend.mcp.tools import add_task as mcp_add_task
        result = await mcp_add_task(user_id, title, description, db)
        return {
            "success": True,
            "confirmation": f"✅ Task added: {title}"
        }
```

**Usage:**
```python
agent = ReusableAgent(adapter=TodoDomainAdapter())
await agent.process_message(user_id, "Add buy milk", [], db)
# → "✅ Task added: Buy milk"
```

### Example 2: CRM System (Example Included)

**Domain:** Professional customer relationship management

**Code:**
```python
# backend/agents/reusable/adapters/crm_adapter.py

class CRMDomainAdapter(DomainAdapter):
    def get_system_prompt(self):
        return """You are a professional CRM Assistant.
        Help sales teams manage contacts, deals, and interactions.
        Maintain professional tone (no emojis)."""

    def get_tools(self):
        return [
            {"type": "function", "function": {
                "name": "create_contact",
                "description": "Create customer contact",
                # ...
            }},
            {"type": "function", "function": {
                "name": "create_deal",
                "description": "Create sales opportunity",
                # ...
            }}
        ]

    async def _create_contact_handler(self, user_id, name, email, company, db=None):
        # CRM contact creation logic
        return {
            "success": True,
            "message": f"Contact created: {name} ({company})"
        }
```

**Usage:**
```python
crm_agent = ReusableAgent(adapter=CRMDomainAdapter())
await crm_agent.process_message(user_id, "Create contact John Doe at Acme Corp", [], db)
# → "Contact created: John Doe (Acme Corp)"
```

**Key Difference from Todo:**
- Professional tone (no emojis)
- Different tools (contacts vs tasks)
- Different formatting
- **Same underlying agent architecture!**

### Example 3: Weather Assistant (Exercise)

Build a weather assistant with these tools:
- `get_current_weather(city)`
- `get_forecast(city, days)`

**Hints:**
```python
class WeatherDomainAdapter(DomainAdapter):
    def get_system_prompt(self):
        return """You are a friendly Weather Assistant.
        Use weather emojis: ☀️ sunny, 🌧️ rain, ❄️ snow, ⛅ cloudy"""

    def get_tools(self):
        return [
            {"type": "function", "function": {
                "name": "get_current_weather",
                # Define parameters: city (string, required)
            }}
        ]

    async def _get_current_weather(self, user_id, city, db=None):
        # Call weather API (OpenWeatherMap, WeatherAPI, etc.)
        # Or use placeholder for demo
        return {
            "city": city,
            "temperature": "20°C",
            "condition": "sunny",
            "emoji": "☀️"
        }
```

---

## Migration Guide

### Before: Original todo_agent.py (568 lines)

```python
# backend/agents/todo_agent.py

AGENT_SYSTEM_PROMPT = """You are a friendly Todo Assistant..."""

async def add_task_tool(...):
    # 50 lines of code

async def list_tasks_tool(...):
    # 50 lines of code

# ... more tools

tools = [
    {"type": "function", "function": {...}},
    # ... 5 tool definitions
]

async def run_todo_agent(user_id, message, conversation_history, db):
    # Hard-coded system prompt
    # Hard-coded tool definitions
    # Hard-coded tool dispatch (if/elif/else for each tool)
    # 100+ lines of OpenAI orchestration
    pass
```

### After: Using Reusable Framework (10 lines)

```python
# backend/agents/todo_agent.py (NEW)

from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

# Create singleton
todo_agent = ReusableAgent(adapter=TodoDomainAdapter())

async def run_todo_agent(user_id, message, conversation_history, db):
    """Run Todo Agent using reusable framework"""
    return await todo_agent.process_message(user_id, message, conversation_history, db)
```

**All Todo logic moved to:** `backend/agents/reusable/adapters/todo_adapter.py`

**Benefits:**
- 98% code reduction (568 → 10 lines)
- Separation of concerns
- Reusable architecture
- Easier to test
- Same functionality

---

## Best Practices

### 1. System Prompts

✅ **DO:**
```python
def get_system_prompt(self):
    return """You are a [clear role] that helps with [specific domain].

**Capabilities:**
- [Specific capability 1]
- [Specific capability 2]

**Response Style:**
- [Clear guideline 1]
- [Example of expected output]

**Important Rules:**
- [Critical constraint 1]
- [Critical constraint 2]
"""
```

❌ **DON'T:**
```python
def get_system_prompt(self):
    return "You are an AI assistant."  # Too vague!
```

### 2. Tool Design

✅ **DO:**
- One tool = one responsibility
- Validate inputs in handler
- Return structured data
- Include success/error flags

```python
async def _add_task_handler(self, user_id, title, db=None):
    # Validation
    if not title.strip():
        return {"error": True, "message": "Title required"}

    # Business logic
    result = await mcp_add_task(...)

    # Structured response
    return {
        "success": True,
        "task_id": result["id"],
        "confirmation": f"✅ Task added: {title}"
    }
```

❌ **DON'T:**
```python
async def _kitchen_sink_handler(self, user_id, action, data1, data2, ..., db=None):
    # One tool doing multiple things - hard to maintain!
    if action == "add":
        # ...
    elif action == "update":
        # ...
    # ...
```

### 3. Response Formatting

✅ **DO:**
```python
def format_response(self, response, context):
    # Add domain-specific formatting
    if context.get("tool_calls"):
        # Add visual indicators
        response = f"🔧 {response}"
    return response
```

❌ **DON'T:**
```python
def format_response(self, response, context):
    # Over-engineer formatting
    # 200 lines of complex string manipulation
    # Just keep it simple!
```

### 4. Error Handling

✅ **DO:**
```python
def handle_error(self, error, context):
    # User-friendly message
    if isinstance(error, ValueError):
        return f"⚠️ Invalid input: {str(error)}"
    return "I encountered an error. Please try again."
```

❌ **DON'T:**
```python
def handle_error(self, error, context):
    # Expose internal details
    return f"Exception in line 42: {error.__traceback__}"
```

### 5. Testing

✅ **DO:** Test adapters independently
```python
def test_todo_adapter():
    adapter = TodoDomainAdapter()

    # Test configuration
    assert "Todo Assistant" in adapter.get_system_prompt()
    assert len(adapter.get_tools()) == 5
    assert "add_task" in adapter.get_tool_handlers()

    # Test greeting
    assert adapter.is_greeting("hello")
    assert "👋" in adapter.get_greeting_response()
```

---

## FAQ

### Q: Do I have to migrate existing code?

**A:** No! The original `todo_agent.py` still works. The reusable framework is for:
- New projects
- Learning the architecture
- Creating multi-domain systems

### Q: Can I use both old and new code together?

**A:** Yes! You can run both:
```python
# Old code
from backend.agents.todo_agent import run_todo_agent

# New code
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter
```

### Q: What if I need custom behavior not in the adapter?

**A:** Three options:
1. Override adapter methods
2. Use `agent.add_tool()` for dynamic tools
3. Create custom adapter subclass

### Q: Is there a performance impact?

**A:** No. Same OpenAI API calls, just better organized.

### Q: How do I share adapters between projects?

**A:** Extract to separate package:
```python
# my-agents-package/adapters/todo_adapter.py
class TodoDomainAdapter(DomainAdapter):
    # ...

# Install in multiple projects
pip install my-agents-package

# Use anywhere
from my_agents.adapters import TodoDomainAdapter
```

### Q: Can I combine multiple domains in one agent?

**A:** Yes! Create a multi-skill adapter:
```python
class MultiSkillAdapter(DomainAdapter):
    def get_tools(self):
        return (
            TodoDomainAdapter().get_tools() +
            WeatherAdapter().get_tools()
        )

    def get_tool_handlers(self):
        return {
            **TodoDomainAdapter().get_tool_handlers(),
            **WeatherAdapter().get_tool_handlers()
        }
```

### Q: What about authentication/authorization?

**A:** Handle in tool handlers:
```python
async def _admin_tool_handler(self, user_id, db=None, **kwargs):
    # Check permissions
    if not await is_admin(user_id, db):
        return {"error": True, "message": "Unauthorized"}

    # Proceed with operation
    # ...
```

---

## File Structure

```
backend/agents/reusable/
├── __init__.py                 # Package exports
├── core/
│   └── reusable_agent.py       # Generic agent (works with any adapter)
├── adapters/
│   ├── base_adapter.py         # Abstract adapter interface
│   ├── todo_adapter.py         # Todo domain configuration
│   └── crm_adapter.py          # CRM domain configuration (example)
├── MIGRATION_GUIDE.md          # How to migrate from old code
└── utils/                      # Shared utilities (future)
```

---

## Next Steps

1. ✅ Review the architecture
2. ✅ Examine `TodoDomainAdapter` to understand extraction
3. ✅ Try creating a simple adapter (Weather example above)
4. 🚀 Build your own domain adapter
5. 🚀 Share your adapter with the community

---

## Summary

**What you learned:**

1. **Architecture:** ReusableAgent + DomainAdapter + MCP Tools
2. **Benefits:** Code reuse, separation of concerns, testability
3. **How to create adapters:** Implement 3 required methods
4. **Examples:** Todo (friendly), CRM (professional), Weather (exercise)
5. **Migration:** Optional, backwards compatible

**Key Insight:** Same agent architecture, infinite domains!

**You can now build AI agents for ANY domain in ~100 lines of code.** 🎉

---

## Resources

- **Code:** `/home/umair/todo-chatbot/backend/agents/reusable/`
- **Examples:** `todo_adapter.py`, `crm_adapter.py`
- **Migration:** `MIGRATION_GUIDE.md`
- **OpenAI Docs:** https://platform.openai.com/docs/guides/function-calling

**Questions? Open an issue on GitHub!**
