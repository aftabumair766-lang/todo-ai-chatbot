# Todo AI Agent - Example Responses

**Agent**: Enhanced with beginner-friendly features
**Architecture**: Stateless, MCP-First
**Constitution Compliance**: ✅ All principles maintained

---

## Feature 1: Action Confirmation Messages

### Add Task
**User**: "Add a task to buy groceries"
**Agent**: "✅ Task added: Buy groceries"

**User**: "Remember to call mom"
**Agent**: "✅ Task added: Call mom"

### Complete Task
**User**: "Mark task 1 as complete"
**Agent**: "✅ Task completed: Buy groceries"

**User**: "I finished the report"
**Agent**: "✅ Task completed: Send report"

### Delete Task
**User**: "Delete task 3"
**Agent**: "🗑️ Task deleted: Old meeting"

**User**: "Remove the shopping task"
**Agent**: "🗑️ Task deleted: Shopping"

### Update Task
**User**: "Change task 2 to 'Buy groceries and fruits'"
**Agent**: "✏️ Task updated: Buy groceries and fruits"

**User**: "Update the description of task 1 to 'Call mom at 6pm'"
**Agent**: "✏️ Task updated: Call mom"

---

## Feature 2 & 3: Task Status Emoji + Neat Task List

### List All Tasks
**User**: "Show me all my tasks"
**Agent**:
```
Your tasks:
1. ⏳ Buy groceries (pending)
2. ✅ Send report (completed)
3. ⏳ Call mom (pending)
```

### List Pending Tasks
**User**: "What's pending?"
**Agent**:
```
Your tasks:
1. ⏳ Buy groceries (pending)
2. ⏳ Call mom (pending)
```

### List Completed Tasks
**User**: "What have I completed?"
**Agent**:
```
Your tasks:
1. ✅ Send report (completed)
```

### Empty Task List
**User**: "Show me my tasks"
**Agent**: "You don't have any tasks yet. Want to add one?"

---

## Feature 4: Basic Input Validation

### Empty Title Rejection
**User**: "Add a task"
**Agent**: "⚠️ Task title cannot be empty. Please provide a name for your task."

**User**: "Create a task with title ''"
**Agent**: "⚠️ Task title cannot be empty. Please provide a name for your task."

### Task Not Found
**User**: "Delete task 999"
**Agent**: "⚠️ I couldn't find task 999. Would you like to see your current tasks?"

**User**: "Mark task 888 as done"
**Agent**: "⚠️ I couldn't find task 888. Would you like to see your current tasks?"

### Already Completed
**User**: "Mark task 2 as complete" (when already completed)
**Agent**: "⚠️ Task 2 is already complete!"

### Missing Update Fields
**User**: "Update task 1" (without specifying what to update)
**Agent**: "⚠️ Please provide at least a new title or description to update."

---

## Feature 5: Greetings & Small Talk

### Simple Greetings
**User**: "Hi"
**Agent**: "👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

**User**: "Hello"
**Agent**: "👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

**User**: "Hey"
**Agent**: "👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

**User**: "Good morning"
**Agent**: "👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

---

## Full Conversation Example

**User**: "Hi"
**Agent**: "👋 Hello! I'm your Todo Assistant. Ready to help you manage your tasks today! You can ask me to add, view, complete, update, or delete tasks."

**User**: "Add a task to buy groceries"
**Agent**: "✅ Task added: Buy groceries"

**User**: "Add a task to call mom"
**Agent**: "✅ Task added: Call mom"

**User**: "Show me all my tasks"
**Agent**:
```
Your tasks:
1. ⏳ Buy groceries (pending)
2. ⏳ Call mom (pending)
```

**User**: "Mark task 1 as complete"
**Agent**: "✅ Task completed: Buy groceries"

**User**: "What's pending?"
**Agent**:
```
Your tasks:
1. ⏳ Call mom (pending)
```

**User**: "Update task 2 description to 'Call mom at 6pm today'"
**Agent**: "✏️ Task updated: Call mom"

**User**: "Delete task 2"
**Agent**: "🗑️ Task deleted: Call mom"

**User**: "Show me my tasks"
**Agent**: "You don't have any tasks yet. Want to add one?"

---

## Error Handling Examples

### Database Connection Error
**User**: "Add a task to pay bills"
**Agent**: "⚠️ I'm having trouble connecting right now. Please try again in a moment."

### OpenAI API Error
**User**: "Show me my tasks"
**Agent**: "⚠️ I encountered an error: [error message]. Please try again."

### Cross-User Access (Prevented)
**Scenario**: User tries to access task from another user
**Agent**: "⚠️ I couldn't find that task. Would you like to see your current tasks?"
*(Task not found because database query filters by user_id)*

---

## Stateless Architecture Validation

### Server Restart Test
**Before Restart**:
**User**: "Add a task to buy groceries"
**Agent**: "✅ Task added: Buy groceries"

**User**: "Add a task to call mom"
**Agent**: "✅ Task added: Call mom"

**[SERVER RESTART - All in-memory state cleared]**

**After Restart**:
**User**: "Show me my tasks"
**Agent**:
```
Your tasks:
1. ⏳ Buy groceries (pending)
2. ⏳ Call mom (pending)
```
*(Conversation history and tasks loaded from database - stateless architecture working)*

---

## Constitution Compliance Confirmation

### ✅ Principle I: MCP-First Architecture
- All task operations use MCP tool wrappers
- Agent never accesses database directly
- Tools: add_task, list_tasks, complete_task, delete_task, update_task

### ✅ Principle II: Stateless Server Design
- No in-memory conversation storage
- Conversation history loaded from database on every request
- Server restart test passes

### ✅ Principle III: Test-First Development
- Enhanced features follow existing test contracts
- Input validation testable via unit tests

### ✅ Principle IV: Security First
- User_id filtering maintained in all MCP tools
- Input validation prevents empty titles
- No cross-user data access

### ✅ Principle V: Database as Source of Truth
- All state persisted to PostgreSQL
- Enhanced formatting purely presentational (no new state)

### ✅ Principle VI: API Contract Clarity
- Enhanced responses follow existing API schema
- Tool_calls array still includes all MCP invocations

---

## Integration Instructions

1. **Replace** `backend/agents/todo_agent.py` with enhanced version
2. **No database changes required** - purely agent-level enhancements
3. **No MCP tool modifications** - wrappers add formatting only
4. **Test** with example conversations above
5. **Validate** stateless architecture with server restart test

---

## Demo Script (Presentation-Ready)

```python
# Demo 1: Greeting & Add Tasks
User: "Hi"
# → Shows friendly greeting with emoji

User: "Add a task to buy groceries"
# → Confirmation with ✅ emoji

User: "Add a task to call mom"
# → Confirmation with ✅ emoji

# Demo 2: View Tasks with Emoji
User: "Show me all my tasks"
# → Numbered list with ⏳ emoji for pending tasks

# Demo 3: Complete Task
User: "Mark task 1 as complete"
# → Confirmation with ✅ emoji

User: "What's pending?"
# → Shows only pending tasks with ⏳ emoji

# Demo 4: Input Validation
User: "Add a task" (no title)
# → Polite error message with ⚠️ emoji

# Demo 5: Delete Task
User: "Delete task 2"
# → Confirmation with 🗑️ emoji

# Demo 6: Stateless Architecture
# Restart server, then:
User: "Show me my tasks"
# → All tasks still there (loaded from database)
```

---

**Status**: ✅ All enhancements implemented
**Compatibility**: ✅ Maintains full backward compatibility
**Testing**: Ready for unit tests, integration tests, E2E demos
