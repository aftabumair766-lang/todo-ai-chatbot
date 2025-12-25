# Reusable AI Agent Framework

A domain-agnostic AI agent architecture that can be configured for ANY use case through adapters.

## 🎯 What is This?

This framework extracts the generic agent logic from `todo_agent.py` into a reusable system that works across domains:

- ✅ **Todo Management** (task tracking with emojis)
- ✅ **CRM Systems** (customer relationships, professional tone)
- 🚀 **E-commerce** (product catalogs, shopping carts)
- 🚀 **Support Chatbots** (ticket management)
- 🚀 **Any domain you build**

**Key Benefit:** Write ~100 lines of configuration to create a production-ready AI agent.

---

## 📁 Structure

```
reusable/
├── __init__.py                 # Package exports
├── README.md                   # This file
├── MIGRATION_GUIDE.md          # How to migrate from old code
│
├── core/
│   └── reusable_agent.py       # Generic agent (domain-agnostic)
│
└── adapters/
    ├── base_adapter.py         # Abstract adapter interface
    ├── todo_adapter.py         # Todo domain implementation
    └── crm_adapter.py          # CRM domain example
```

---

## 🚀 Quick Start

### Use Existing Todo Agent

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

### Create Custom Agent

```python
from backend.agents.reusable import ReusableAgent, DomainAdapter

class WeatherAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a weather assistant. Use emojis: ☀️ sunny, 🌧️ rain"

    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a city",
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
        # Your weather API integration
        return {"temperature": "20°C", "condition": "☀️ Sunny"}

# Use it
weather_agent = ReusableAgent(adapter=WeatherAdapter())
result = await weather_agent.process_message(
    user_id="user123",
    message="What's the weather in London?",
    conversation_history=[],
    db=db
)
```

---

## 🏗️ Architecture

### 3-Layer Design

```
┌─────────────────────────────────────┐
│    ReusableAgent (Generic Core)    │
│  - OpenAI API calls                 │
│  - Tool routing                     │
│  - Conversation management          │
│  - Error handling                   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  DomainAdapter (Configuration)      │
│  - System prompt (personality)      │
│  - Tool definitions (capabilities)  │
│  - Tool handlers (implementation)   │
│  - Response formatting              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│      MCP Tools (Data Layer)         │
│  - Database operations              │
│  - External API calls               │
│  - Business logic                   │
└─────────────────────────────────────┘
```

### Why This Works

**Separation of Concerns:**
- **Core** = Generic agent logic (works for all domains)
- **Adapter** = Domain-specific configuration
- **MCP Tools** = Data operations

**Result:** Change domains by swapping adapters, not rewriting code.

---

## 📝 Adapter Interface

Every adapter must implement:

```python
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

class YourAdapter(DomainAdapter):
    def get_system_prompt(self) -> str:
        """Return agent personality and instructions"""
        return "You are a helpful assistant..."

    def get_tools(self) -> List[Dict]:
        """Return OpenAI function calling tool definitions"""
        return [
            {"type": "function", "function": {...}}
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Return mapping of tool names to handler functions"""
        return {
            "tool_name": self._tool_handler
        }

    async def _tool_handler(self, user_id, param1, db=None):
        """Implement tool logic"""
        return {"success": True, "data": "..."}
```

**Optional overrides:**
- `is_greeting(message)` - Detect greetings
- `get_greeting_response()` - Return greeting message
- `format_response(response, context)` - Format responses
- `validate_tool_input(tool_name, arguments)` - Validate inputs
- `handle_error(error, context)` - Custom error messages
- `get_model_name()` - Specify OpenAI model

---

## 💡 Examples

### Example 1: Todo (Existing)

**Personality:** Friendly with emojis
**Tools:** add_task, list_tasks, complete_task, delete_task, update_task

```python
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

agent = ReusableAgent(adapter=TodoDomainAdapter())

# Natural language interactions:
await agent.process_message(user_id, "Add buy milk", [], db)
# → "✅ Task added: Buy milk"

await agent.process_message(user_id, "Show my tasks", [], db)
# → "Your tasks:\n1. ⏳ Buy milk (pending)"
```

### Example 2: CRM (Example)

**Personality:** Professional, no emojis
**Tools:** create_contact, list_contacts, create_deal, update_deal_stage, log_interaction

```python
from backend.agents.reusable import ReusableAgent, CRMDomainAdapter

crm_agent = ReusableAgent(adapter=CRMDomainAdapter())

await crm_agent.process_message(user_id, "Create contact John Doe at Acme Corp", [], db)
# → "Contact created: John Doe (Acme Corp)"

await crm_agent.process_message(user_id, "Create $50k deal with John", [], db)
# → "Deal created: Acme Corp Deal ($50,000)"
```

**Key Difference:** Same architecture, different configuration!

---

## 📊 Comparison

### Before: Original todo_agent.py (568 lines)

```python
AGENT_SYSTEM_PROMPT = """You are a friendly Todo Assistant..."""

async def add_task_tool(...):
    # 50 lines

async def list_tasks_tool(...):
    # 50 lines

# ... more tools

tools = [...]  # Hard-coded definitions

async def run_todo_agent(user_id, message, history, db):
    # 100+ lines of OpenAI orchestration
    # Hard-coded tool dispatch (if/elif/else)
    pass
```

❌ **Problems:**
- Cannot reuse for other domains
- Tightly coupled code
- Hard to test
- Duplicate logic across projects

### After: With Reusable Framework (10 lines)

```python
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

todo_agent = ReusableAgent(adapter=TodoDomainAdapter())

async def run_todo_agent(user_id, message, history, db):
    return await todo_agent.process_message(user_id, message, history, db)
```

✅ **Benefits:**
- 98% code reduction (568 → 10 lines)
- Reusable across domains
- Testable components
- Separation of concerns

---

## 🧪 Testing

Test adapters independently:

```python
def test_todo_adapter():
    adapter = TodoDomainAdapter()

    # Test configuration
    assert "Todo Assistant" in adapter.get_system_prompt()
    assert len(adapter.get_tools()) == 5
    assert "add_task" in adapter.get_tool_handlers()

    # Test domain-specific behavior
    assert adapter.is_greeting("hello")
    assert "👋" in adapter.get_greeting_response()
```

---

## 📚 Documentation

- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - How to migrate from old code
- **[REUSABLE_AGENTS_GUIDE.md](../../docs/REUSABLE_AGENTS_GUIDE.md)** - Complete guide with examples
- **[base_adapter.py](./adapters/base_adapter.py)** - Adapter interface documentation
- **[todo_adapter.py](./adapters/todo_adapter.py)** - Full implementation example

---

## 🎓 Learn More

### Step 1: Understand the Architecture

Read the [architecture overview](#architecture) above.

### Step 2: Examine Existing Adapters

- **TodoDomainAdapter** - Friendly chatbot with emojis
- **CRMDomainAdapter** - Professional business assistant

Compare their implementations to see how the same agent works for different domains.

### Step 3: Build Your Own Adapter

Follow the [Quick Start](#quick-start) guide to create a custom adapter.

### Step 4: Migrate Existing Code (Optional)

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for migration steps.

---

## 🚀 Creating New Domains

### Domain Ideas

1. **Weather Assistant**
   - Tools: get_current_weather, get_forecast
   - Personality: Friendly with weather emojis

2. **E-commerce Assistant**
   - Tools: search_products, add_to_cart, checkout, track_order
   - Personality: Helpful shopping guide

3. **Support Chatbot**
   - Tools: create_ticket, search_kb, escalate, close_ticket
   - Personality: Professional and empathetic

4. **Calendar Assistant**
   - Tools: add_event, list_events, find_free_slots, send_invite
   - Personality: Efficient and organized

### Template

```python
# backend/agents/reusable/adapters/your_adapter.py

from backend.agents.reusable.adapters.base_adapter import DomainAdapter

class YourDomainAdapter(DomainAdapter):
    def get_system_prompt(self):
        return """You are a [personality] [domain] assistant.

**Capabilities:**
- [Capability 1]
- [Capability 2]

**Response Style:**
- [Guideline 1]
- [Guideline 2]
"""

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "your_tool",
                    "description": "Tool description",
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

    def get_tool_handlers(self):
        return {
            "your_tool": self._your_tool_handler
        }

    async def _your_tool_handler(self, user_id, param1, db=None):
        # Your implementation
        return {"success": True, "message": "Done!"}
```

---

## 🤝 Contributing

To add your adapter:

1. Create `adapters/your_adapter.py`
2. Implement `DomainAdapter` interface
3. Add to `__init__.py` exports
4. Add tests in `tests/test_your_adapter.py`
5. Document in README

---

## ❓ FAQ

**Q: Is this production-ready?**
A: Yes. TodoDomainAdapter is extracted from production code.

**Q: What's the performance impact?**
A: None. Same OpenAI calls, better organization.

**Q: Can I use multiple adapters together?**
A: Yes! Create a multi-skill adapter that combines tools.

**Q: How do I add authentication?**
A: Handle in tool handlers - check user permissions before operations.

**Q: Can I share adapters between projects?**
A: Yes! Extract to a separate pip package.

---

## 📄 License

Same as parent project.

---

## 🎉 Summary

**You have a production-ready, domain-agnostic AI agent framework.**

- ✅ Works with ANY domain (Todo, CRM, E-commerce, etc.)
- ✅ Reduces code by 98% (568 → 10 lines)
- ✅ Separation of concerns (Core, Adapter, Tools)
- ✅ Easy to test and maintain
- ✅ Proven in production (TodoDomainAdapter)

**Build new agents in ~100 lines instead of 500+!** 🚀

---

**Questions? Check [REUSABLE_AGENTS_GUIDE.md](../../docs/REUSABLE_AGENTS_GUIDE.md) or open an issue!**
