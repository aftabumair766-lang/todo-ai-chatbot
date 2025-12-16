# Quick Start: Using Your Agent in Other Projects

## 🎯 What You Have

Your Todo AI Chatbot contains **2 reusable agents**:

1. **`base_agent.py`** - Generic agent for ANY domain (e-commerce, calendar, healthcare, etc.)
2. **`todo_agent.py`** - Specialized todo task management agent

Both are **production-ready** and can be used in other projects immediately!

---

## 🚀 3 Ways to Reuse Your Agent

### Method 1: Copy Files (Fastest - 2 minutes)

```bash
# In your new project
mkdir -p new-project/agents

# Copy the agent files
cp todo-chatbot/backend/agents/base_agent.py new-project/agents/
cp todo-chatbot/backend/agents/todo_agent.py new-project/agents/  # Optional

# Install dependencies
pip install openai sqlalchemy pydantic

# Use it!
from agents.base_agent import BaseAgent
```

### Method 2: Python Package (Recommended - 5 minutes)

```bash
# Package your agent
cd todo-chatbot
./scripts/package_agent.sh

# Install in other projects
cd dist/todo-agent
pip install -e .

# Now use it anywhere
from todo_agent import run_todo_agent, BaseAgent
```

### Method 3: Git Submodule (For Multiple Projects)

```bash
# In your new project
git submodule add https://github.com/you/todo-agent.git agents

# Import and use
from agents.base_agent import BaseAgent
```

---

## 📖 Usage Examples

### Example 1: Use in E-Commerce Project

```python
from backend.agents.base_agent import BaseAgent
import os

# Define e-commerce tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create customer order",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {"type": "array", "items": {"type": "string"}},
                    "quantities": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["product_ids", "quantities"]
            }
        }
    }
]

# Define handler
async def create_order_handler(user_id, product_ids, quantities, db=None):
    # Your order creation logic
    return {"success": True, "order_id": "ORD123"}

# Create agent
shop_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt="You are ShopBot, an e-commerce assistant.",
    tools=tools,
    tool_handlers={"create_order": create_order_handler}
)

# Use it
result = await shop_agent.process_message(
    user_message="I want to buy product ABC",
    user_id="customer_123",
    conversation_history=[],
    db=db_session
)

print(result["response"])  # AI-generated friendly response
```

### Example 2: Calendar Agent in 10 Lines

```python
from backend.agents.base_agent import BaseAgent

# Just define your tools and handlers
async def book_appointment(user_id, date, time, db=None):
    return {"success": True, "appointment_id": "APT123"}

calendar_agent = BaseAgent(
    api_key="sk-...",
    tools=[{...}],  # Your calendar tools
    tool_handlers={"book_appointment": book_appointment}
)

# Done! Use it like the todo agent
```

---

## 🎨 Customization Guide

### Change Agent Personality

```python
agent = BaseAgent(
    api_key="sk-...",
    system_prompt="You are FriendlyBot, always use emoji and be casual! 😊",
    # ... rest stays the same
)
```

### Add Greeting Detection

```python
def is_greeting(message):
    return message.lower() in ["hi", "hello", "hey"]

agent = BaseAgent(
    api_key="sk-...",
    greeting_detector=is_greeting,
    greeting_response="Hey there! 👋 What can I do for you?"
)
```

### Use Different Models

```python
# Use GPT-3.5 for cost savings
agent = BaseAgent(
    api_key="sk-...",
    model="gpt-3.5-turbo",  # Cheaper, faster
    temperature=0.5  # More deterministic
)

# Use GPT-4 for complex tasks
agent = BaseAgent(
    model="gpt-4-turbo-preview",  # Best quality
    temperature=0.7  # More creative
)
```

### Dynamic Tool Addition

```python
# Start with basic tools
agent = BaseAgent(tools=[tool1, tool2], ...)

# Add more tools later
agent.add_tool(
    tool_definition={...},
    handler=my_new_handler
)

# Remove tools
agent.remove_tool("tool_name")
```

---

## 📂 Project Structure

Your reusable agent files:

```
todo-chatbot/
├── backend/agents/
│   ├── base_agent.py          ⭐ Generic agent (use anywhere!)
│   ├── todo_agent.py          ⭐ Todo-specific agent
│   └── __init__.py
├── docs/
│   ├── AGENT_REUSABILITY_GUIDE.md      📖 Complete guide
│   ├── AGENT_USAGE_EXAMPLES.md         📖 10+ examples
│   └── QUICK_START_REUSABLE_AGENT.md   📖 This file
└── scripts/
    └── package_agent.sh        🎁 Package for distribution
```

---

## 🎓 Learn More

1. **Full Guide**: `docs/AGENT_REUSABILITY_GUIDE.md`
   - Packaging methods
   - Publishing to PyPI
   - Finding other agents

2. **Usage Examples**: `docs/AGENT_USAGE_EXAMPLES.md`
   - E-commerce agent
   - Calendar agent
   - Support ticket agent
   - Healthcare agent

3. **OpenAI Docs**: https://platform.openai.com/docs/guides/function-calling

---

## ✅ Quick Checklist

To use your agent in a new project:

- [ ] Copy `base_agent.py` to new project
- [ ] Install dependencies: `pip install openai sqlalchemy pydantic`
- [ ] Define your tools (OpenAI function calling format)
- [ ] Implement tool handlers (async functions)
- [ ] Create BaseAgent instance
- [ ] Call `agent.process_message()`
- [ ] Enjoy! 🎉

**Your agent works with ANY domain - just change the tools!**

---

## 🆘 Common Questions

**Q: Can I use this without the todo tools?**
A: Yes! Use `BaseAgent` with your own tools. Todo agent is just one example.

**Q: Does this work with FastAPI?**
A: Yes! See `backend/api/chat.py` for integration example.

**Q: Can I use GPT-3.5 instead of GPT-4?**
A: Yes! Just set `model="gpt-3.5-turbo"` when creating the agent.

**Q: How do I add my own database?**
A: Pass your `db` session to `process_message()` - it's forwarded to all tool handlers.

**Q: Can I deploy this to production?**
A: Absolutely! It's production-ready with proper error handling and logging.

---

## 🚀 Next Steps

1. Try the examples in `docs/AGENT_USAGE_EXAMPLES.md`
2. Package your agent with `./scripts/package_agent.sh`
3. Use it in your next project!

**Your agent is ready to power ANY application!** 🎉
