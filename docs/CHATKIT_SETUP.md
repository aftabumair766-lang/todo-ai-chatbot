# OpenAI ChatKit Setup Guide

This guide will help you complete the ChatKit integration for your Todo AI Chatbot.

## Prerequisites

- OpenAI account with API access
- Access to OpenAI Platform Dashboard
- API key already configured (✅ Already done)

## Step 1: Create Workflow in OpenAI Platform

### 1.1 Access OpenAI Platform
1. Go to https://platform.openai.com
2. Log in with your OpenAI account
3. Navigate to the **Workflows** or **Assistants** section

### 1.2 Create New Workflow
Click "Create New Workflow" or "New Assistant"

### 1.3 Configure Workflow Settings

**Basic Information:**
- **Name:** Todo Task Manager
- **Model:** gpt-4-turbo-preview (or latest GPT-4)
- **Description:** AI-powered task management assistant

**Instructions:**
```
You are a friendly Todo Task Assistant that helps users manage their tasks.

Your capabilities:
- Add tasks with natural language
- List and filter tasks (all, pending, completed)
- Complete tasks by ID
- Delete tasks by ID
- Update task titles and descriptions

Always be friendly and use emojis to make the experience engaging.

When users ask to:
- Add a task: Use the add_task function
- Show/list tasks: Use the list_tasks function
- Complete a task: Use the complete_task function
- Delete a task: Use the delete_task function
- Update a task: Use the update_task function
```

### 1.4 Add Functions/Tools

Copy the tool definitions from `docs/chatkit-workflow-tools.json` and add each function:

**Function 1: add_task**
```json
{
  "name": "add_task",
  "description": "Add a new task to the user's todo list",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required, max 500 chars)"
      },
      "description": {
        "type": "string",
        "description": "Optional task description (max 2000 chars)"
      }
    },
    "required": ["title"]
  }
}
```

**Function 2: list_tasks**
```json
{
  "name": "list_tasks",
  "description": "List user's tasks with optional filtering by status",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter tasks by status (default: all)"
      }
    },
    "required": []
  }
}
```

**Function 3: complete_task**
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of the task to complete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Function 4: delete_task**
```json
{
  "name": "delete_task",
  "description": "Delete a task from the user's list",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of the task to delete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Function 5: update_task**
```json
{
  "name": "update_task",
  "description": "Update a task's title and/or description",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New task title (optional)"
      },
      "description": {
        "type": "string",
        "description": "New task description (optional)"
      }
    },
    "required": ["task_id"]
  }
}
```

### 1.5 Save and Get Workflow ID

After creating the workflow:
1. Click "Save" or "Create"
2. **Copy the Workflow ID** (it will look like: `asst_xxxxxxxxxxxxx` or `wf_xxxxxxxxxxxxx`)
3. Save this ID - you'll need it for the next step

## Step 2: Update Backend Configuration

Add the workflow ID to your `.env` file:

```bash
# Add this line to backend/.env
CHATKIT_WORKFLOW_ID=your_workflow_id_here
```

Replace `your_workflow_id_here` with the actual workflow ID you copied.

## Step 3: Restart the Application

```bash
# Stop the current backend
pkill -f "uvicorn backend.main:app"

# Restart with new configuration
cd /home/umair/todo-chatbot
./quick-start.sh
```

## Step 4: Test ChatKit

1. Open http://localhost:5173
2. Enter "test" as the authentication token
3. You should now see the ChatKit interface
4. Try chatting: "Add a task to buy groceries"

## Troubleshooting

### Error: "Missing required parameter: 'workflow.id'"
- Make sure you added `CHATKIT_WORKFLOW_ID` to `.env`
- Restart the backend after adding the variable

### Error: "Workflow not found"
- Verify the workflow ID is correct
- Check that the workflow exists in your OpenAI account

### Tools not working
- Verify you added all 5 functions to the workflow
- Check that function names match exactly (case-sensitive)

## Architecture Notes

**How it works:**
1. Frontend calls `/api/chatkit/session` to create a session
2. Backend creates a ChatKit session with your workflow ID
3. ChatKit returns a client secret
4. Frontend uses ChatKit UI components with the client secret
5. When user chats, ChatKit calls your workflow
6. Workflow invokes functions which call your MCP tools
7. Results are returned to the chat

**Function Flow:**
```
User Message → ChatKit → Workflow → Function Call → MCP Tool → Database → Response
```

## Next Steps

Once ChatKit is working:
1. ✅ Test all task operations
2. 🔄 Integrate Better Auth for production authentication
3. 📝 Create production deployment documentation
4. 🚀 Deploy to production

## Support

If you encounter issues:
- Check OpenAI Platform status: https://status.openai.com
- Review OpenAI ChatKit docs: https://platform.openai.com/docs/guides/chatkit
- Check backend logs: `tail -f backend.log`
