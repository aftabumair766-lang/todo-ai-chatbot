# Reusable Agents - Quick Reference Card

## ⚡ 30-Second Start

```python
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

agent = ReusableAgent(adapter=TodoDomainAdapter())
result = await agent.process_message(user_id, message, history, db)
print(result["response"])
```

---

## 🎯 Create Custom Adapter (Minimal)

```python
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

class MyAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a helpful assistant..."

    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "What it does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "Param info"}
                    },
                    "required": ["param"]
                }
            }
        }]

    def get_tool_handlers(self):
        return {"my_tool": self._my_tool_handler}

    async def _my_tool_handler(self, user_id, param, db=None):
        return {"success": True, "message": f"Got {param}"}
```

**Use it:**
```python
agent = ReusableAgent(adapter=MyAdapter())
```

---

## 📋 Adapter Interface Checklist

### Required Methods (3)

- [ ] `get_system_prompt()` → str
- [ ] `get_tools()` → List[Dict]
- [ ] `get_tool_handlers()` → Dict[str, Callable]

### Optional Overrides (6)

- [ ] `is_greeting(message)` → bool
- [ ] `get_greeting_response()` → str
- [ ] `format_response(response, context)` → str
- [ ] `validate_tool_input(tool_name, args)` → Optional[str]
- [ ] `handle_error(error, context)` → str
- [ ] `get_model_name()` → str

---

## 🔧 Tool Definition Template

```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Clear description of what this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",  # or "integer", "boolean", "array", "object"
                    "description": "What this parameter is for"
                },
                "param2": {
                    "type": "integer",
                    "description": "Another parameter"
                }
            },
            "required": ["param1"]  # List required parameters
        }
    }
}
```

**Types:** `string`, `integer`, `number`, `boolean`, `array`, `object`, `null`

**For enums:**
```python
"priority": {
    "type": "string",
    "enum": ["low", "medium", "high"],
    "description": "Priority level"
}
```

---

## 🎭 System Prompt Template

```python
def get_system_prompt(self):
    return """You are a [personality adjectives] [role] that helps users [primary function].

**Your Capabilities:**
- [Capability 1 with context]
- [Capability 2 with context]
- [Capability 3 with context]

**Conversation Style:**
- [Tone guideline 1]
- [Formatting guideline 2]
- [Response structure guideline 3]

**Important Rules:**
- [Critical constraint 1]
- [Critical constraint 2]

**Examples:**
User: [Example user input]
You: [Example response showing style]
"""
```

**Tips:**
- Be specific about capabilities (not "manage tasks", but "add, complete, delete, and update tasks")
- Define output format (e.g., "Use emojis: ✅ = done, ⏳ = pending")
- Include examples of expected responses
- Set clear boundaries ("Never make up task IDs")

---

## 🛠️ Tool Handler Template

```python
async def _tool_name_handler(
    self,
    user_id: str,
    param1: str,
    param2: Optional[int] = None,
    db=None
) -> Dict[str, Any]:
    """
    Tool description.

    Args:
        user_id: User identifier (automatically injected)
        param1: First parameter from OpenAI
        param2: Optional second parameter
        db: Database session (automatically injected)

    Returns:
        Dict with success/error and data
    """
    # 1. Validation
    if not param1.strip():
        return {
            "error": True,
            "message": "param1 is required"
        }

    # 2. Business logic (call MCP tools)
    try:
        from backend.mcp.your_tools import your_mcp_tool
        result = await your_mcp_tool(user_id, param1, param2, db)

        # 3. Return structured response
        return {
            "success": True,
            "data": result,
            "message": "Operation completed successfully"
        }

    except ValueError as e:
        return {"error": True, "message": str(e)}
    except Exception as e:
        logger.error(f"Error in tool: {e}")
        return {"error": True, "message": "Internal error"}
```

**Response Structure:**
```python
# Success
{"success": True, "data": {...}, "message": "Confirmation"}

# Error
{"error": True, "message": "User-friendly error message"}
```

---

## 📁 File Locations

```
backend/agents/reusable/
├── __init__.py                    # Import from here
├── core/
│   └── reusable_agent.py          # ReusableAgent class
└── adapters/
    ├── base_adapter.py            # DomainAdapter interface
    ├── todo_adapter.py            # Example: Todo
    ├── crm_adapter.py             # Example: CRM
    └── your_adapter.py            # Your adapter here
```

---

## 🎨 Example Adapters

### Minimal Adapter (No Tools)

```python
class EchoAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are an echo assistant. Repeat what users say."

    def get_tools(self):
        return []  # No tools

    def get_tool_handlers(self):
        return {}
```

### Weather Adapter

```python
class WeatherAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a weather assistant. Use emojis: ☀️☁️🌧️❄️"

    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"]
                }
            }
        }]

    def get_tool_handlers(self):
        return {"get_weather": self._get_weather}

    async def _get_weather(self, user_id, city, db=None):
        # Call weather API or return mock data
        return {"temperature": "20°C", "condition": "☀️ Sunny"}

    def get_greeting_response(self):
        return "☀️ Hi! Ask me about weather in any city!"
```

### Multi-Tool Adapter

```python
class ShoppingAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a shopping assistant."

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_cart",
                    "description": "Add product to cart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "quantity": {"type": "integer"}
                        },
                        "required": ["product_id", "quantity"]
                    }
                }
            }
        ]

    def get_tool_handlers(self):
        return {
            "search_products": self._search_products,
            "add_to_cart": self._add_to_cart
        }

    async def _search_products(self, user_id, query, db=None):
        # Implementation
        pass

    async def _add_to_cart(self, user_id, product_id, quantity, db=None):
        # Implementation
        pass
```

---

## 🧪 Testing Checklist

```python
def test_your_adapter():
    adapter = YourAdapter()

    # Test system prompt
    prompt = adapter.get_system_prompt()
    assert "your expected text" in prompt

    # Test tools configuration
    tools = adapter.get_tools()
    assert len(tools) > 0
    assert tools[0]["function"]["name"] == "expected_tool_name"

    # Test tool handlers
    handlers = adapter.get_tool_handlers()
    assert "expected_tool_name" in handlers

    # Test greeting (if applicable)
    assert adapter.is_greeting("hello") == True
    assert adapter.is_greeting("add task") == False

    # Test greeting response
    greeting = adapter.get_greeting_response()
    assert greeting is not None
    assert len(greeting) > 0
```

---

## 🚀 Common Patterns

### Pattern 1: Inheritance

Extend existing adapter:

```python
class AdvancedTodoAdapter(TodoDomainAdapter):
    def get_tools(self):
        base_tools = super().get_tools()
        base_tools.append({
            "type": "function",
            "function": {"name": "new_tool", ...}
        })
        return base_tools

    def get_tool_handlers(self):
        handlers = super().get_tool_handlers()
        handlers["new_tool"] = self._new_tool_handler
        return handlers
```

### Pattern 2: Multi-Domain

Combine multiple domains:

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

### Pattern 3: Dynamic Tools

Add tools at runtime:

```python
agent = ReusableAgent(adapter=YourAdapter())

# Add tool dynamically
agent.add_tool(
    tool_definition={"type": "function", "function": {...}},
    handler=custom_handler_function
)
```

---

## 🔍 Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In tool handler:
logger.info(f"Tool called with args: {param1}, {param2}")
logger.error(f"Error occurred: {e}")
```

### Check Tool Calls

```python
result = await agent.process_message(user_id, message, history, db)

# Inspect what tools were called
print(result["tool_calls"])
# [
#   {
#     "tool": "add_task",
#     "arguments": {"title": "Buy milk"},
#     "result": {"success": True, "task_id": 123}
#   }
# ]
```

### Validate Configuration

```python
adapter = YourAdapter()

# Check tools are properly defined
print(f"Tools: {len(adapter.get_tools())}")
print(f"Handlers: {list(adapter.get_tool_handlers().keys())}")

# Ensure they match
tool_names = {t["function"]["name"] for t in adapter.get_tools()}
handler_names = set(adapter.get_tool_handlers().keys())
assert tool_names == handler_names, "Tools and handlers mismatch!"
```

---

## 💡 Tips & Tricks

### Tip 1: Use Type Hints

```python
from typing import Dict, List, Callable, Any, Optional

async def _tool_handler(
    self,
    user_id: str,
    param: str,
    db: Optional[Any] = None
) -> Dict[str, Any]:
    ...
```

### Tip 2: Consistent Response Structure

```python
# Always return this structure
{
    "success": True/False,  # or "error": True
    "message": "User-friendly message",
    "data": {...}  # Optional, for structured data
}
```

### Tip 3: Validate Early

```python
async def _tool_handler(self, user_id, title, db=None):
    # Validate immediately
    if not title or not title.strip():
        return {"error": True, "message": "Title is required"}

    # Continue with business logic
    ...
```

### Tip 4: Keep Handlers Simple

```python
async def _add_task_handler(self, user_id, title, db=None):
    # DON'T: Put business logic here
    # DO: Call MCP tools
    from backend.mcp.tools import add_task
    return await add_task(user_id, title, db)
```

---

## 📚 Resources

- **Full Guide:** `docs/REUSABLE_AGENTS_GUIDE.md`
- **Migration:** `MIGRATION_GUIDE.md`
- **Examples:** `adapters/todo_adapter.py`, `adapters/crm_adapter.py`
- **OpenAI Docs:** https://platform.openai.com/docs/guides/function-calling

---

## ✅ Checklist: Creating New Adapter

- [ ] Create `adapters/your_adapter.py`
- [ ] Implement `get_system_prompt()`
- [ ] Implement `get_tools()`
- [ ] Implement `get_tool_handlers()`
- [ ] Implement tool handler methods
- [ ] Add to `__init__.py` exports
- [ ] Test adapter configuration
- [ ] Test tool execution
- [ ] Document in README

---

**Print this card for quick reference while coding!** 🚀
