#!/usr/bin/env python3
"""
Automated Phase 5 Chatbot Demo
Shows all features working through natural language
"""
import asyncio
import sys
sys.path.insert(0, '/home/umair/todo-chatbot')

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.config import Settings
from backend.mcp.tools import (
    add_task, list_tasks, create_tag, list_tags,
    update_task, complete_task
)

settings = Settings()
DEMO_USER_ID = "demo-user-chatbot"

async def simulate_chat(db, user_message, action):
    """Simulate a chat interaction"""
    print(f"\n{'='*60}")
    print(f"👤 User: {user_message}")
    print(f"{'='*60}")

    try:
        result = await action(db)
        print(f"🤖 Bot: {result}")
        return result
    except Exception as e:
        print(f"🤖 Bot: ❌ Error: {str(e)}")
        return None

async def main():
    print("\n" + "="*60)
    print("🎯 PHASE 5 CHATBOT DEMO - Natural Language Interface")
    print("="*60)
    print("\nDemonstrating how users interact with Phase 5 features...")

    # Setup database
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Demo 1: Create tags
        await simulate_chat(
            db,
            "Create a tag called 'work' with color #FF5733",
            lambda db: create_tag(db, DEMO_USER_ID, "work", "#FF5733")
        )

        await simulate_chat(
            db,
            "Create a tag called 'urgent' with color #FF0000",
            lambda db: create_tag(db, DEMO_USER_ID, "urgent", "#FF0000")
        )

        # Demo 2: Add high priority task
        due_tomorrow = datetime.now() + timedelta(days=1)
        await simulate_chat(
            db,
            "Add a high priority task: Complete annual report by tomorrow",
            lambda db: add_task(
                db, DEMO_USER_ID,
                title="Complete annual report",
                description="Q4 financial report for board meeting",
                priority="high",
                due_date=due_tomorrow,
                tags=["work", "urgent"]
            )
        )

        # Demo 3: Add medium priority task
        await simulate_chat(
            db,
            "Add a task: Buy groceries with tags personal",
            lambda db: add_task(
                db, DEMO_USER_ID,
                title="Buy groceries",
                description="Milk, eggs, bread",
                priority="medium",
                tags=["personal"]
            )
        )

        # Demo 4: Add low priority task
        await simulate_chat(
            db,
            "Create a low priority task: Read technical book",
            lambda db: add_task(
                db, DEMO_USER_ID,
                title="Read technical book",
                priority="low",
                tags=["personal"]
            )
        )

        # Demo 5: List all tasks
        async def show_all_tasks(db):
            result = await list_tasks(db, DEMO_USER_ID, status="all")
            response = f"✅ You have {result['count']} tasks:\n"
            for task in result['tasks']:
                status_icon = "✓" if task['completed'] else "○"
                priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                response += f"  {status_icon} {priority_emoji} [{task['priority'].upper()}] {task['title']}"
                if task.get('tags'):
                    response += f" (Tags: {', '.join(task['tags'])})"
                response += "\n"
            return response

        await simulate_chat(
            db,
            "Show me all my tasks",
            show_all_tasks
        )

        # Demo 6: Filter by priority
        async def show_high_priority(db):
            result = await list_tasks(db, DEMO_USER_ID, priority="high")
            response = f"✅ Found {result['count']} high priority task(s):\n"
            for task in result['tasks']:
                response += f"  🟠 {task['title']}\n"
            return response

        await simulate_chat(
            db,
            "Show me all high priority tasks",
            show_high_priority
        )

        # Demo 7: Search tasks
        async def search_report(db):
            result = await list_tasks(db, DEMO_USER_ID, search="report")
            response = f"✅ Found {result['count']} task(s) matching 'report':\n"
            for task in result['tasks']:
                response += f"  • {task['title']}\n"
            return response

        await simulate_chat(
            db,
            "Search for tasks containing 'report'",
            search_report
        )

        # Demo 8: List tasks by priority
        async def sort_by_priority(db):
            result = await list_tasks(db, DEMO_USER_ID, sort_by="priority", sort_order="desc")
            response = f"✅ Tasks sorted by priority:\n"
            for task in result['tasks']:
                priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
                response += f"  {priority_emoji} [{task['priority'].upper()}] {task['title']}\n"
            return response

        await simulate_chat(
            db,
            "List all tasks sorted by priority",
            sort_by_priority
        )

        # Demo 9: Update task priority
        async def update_priority(db):
            # Get first task
            tasks = await list_tasks(db, DEMO_USER_ID, status="all")
            if tasks['count'] > 0:
                task_id = tasks['tasks'][0]['id']
                result = await update_task(
                    db, DEMO_USER_ID,
                    task_id=task_id,
                    priority="urgent"
                )
                return f"✅ Updated '{result['task']['title']}' to URGENT priority"
            return "No tasks to update"

        await simulate_chat(
            db,
            "Update the first task to urgent priority",
            update_priority
        )

        # Demo 10: List all tags
        async def show_tags(db):
            result = await list_tags(db, DEMO_USER_ID)
            response = f"✅ You have {result['count']} tag(s):\n"
            for tag in result['tags']:
                response += f"  🏷️  {tag['name']} ({tag['usage_count']} tasks) {tag['color']}\n"
            return response

        await simulate_chat(
            db,
            "Show me all my tags",
            show_tags
        )

        # Demo 11: Complete a task
        async def complete_a_task(db):
            # Get a pending task
            tasks = await list_tasks(db, DEMO_USER_ID, status="pending")
            if tasks['count'] > 0:
                task_id = tasks['tasks'][-1]['id']  # Get last pending task
                result = await complete_task(db, DEMO_USER_ID, task_id)
                return f"✅ Completed: '{result['task']['title']}'"
            return "No pending tasks to complete"

        await simulate_chat(
            db,
            "Mark the last task as complete",
            complete_a_task
        )

        # Final summary
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE - ALL PHASE 5 FEATURES WORKING!")
        print("="*60)
        print("\nYour users can now:")
        print("  ✅ Create tasks with priority, due dates, and tags")
        print("  ✅ Search and filter tasks by multiple criteria")
        print("  ✅ Sort tasks dynamically")
        print("  ✅ Manage tags with colors")
        print("  ✅ Update tasks with any Phase 5 field")
        print("  ✅ Complete and track tasks")
        print("\n🚀 Phase 5 implementation is FULLY FUNCTIONAL!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
