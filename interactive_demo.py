#!/usr/bin/env python3
"""
Interactive Phase 5 Feature Demo
Follow along and see features in action!
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '/home/umair/todo-chatbot')

from backend.config import Settings
from backend.mcp.tools import (
    add_task, list_tasks, create_tag, list_tags,
    update_task, complete_task, delete_tag
)

settings = Settings()
DEMO_USER = "interactive-demo-user"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(number, title):
    print(f"\n{'─'*70}")
    print(f"📍 STEP {number}: {title}")
    print(f"{'─'*70}")

def wait_for_enter(message="Press ENTER to continue..."):
    input(f"\n⏸️  {message}")

async def main():
    print_header("🎯 INTERACTIVE PHASE 5 DEMO")
    print("\nWelcome! We'll explore all Phase 5 features step by step.")
    print("You'll see each feature in action with real examples.")

    wait_for_enter("Press ENTER to start the demo")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # FEATURE 1: TAGS WITH COLORS
        print_step(1, "Creating Colorful Tags 🏷️")
        print("\n💡 NEW FEATURE: Organize tasks with colored tags")
        print("\nCreating 3 tags:")

        tags_to_create = [
            ("work", "#FF5733", "🔴"),
            ("urgent", "#FF0000", "🔥"),
            ("personal", "#00FF00", "💚"),
        ]

        for tag_name, color, emoji in tags_to_create:
            try:
                tag = await create_tag(db, DEMO_USER, tag_name, color)
                print(f"  ✅ {emoji} Created '{tag_name}' with color {color}")
            except ValueError as e:
                print(f"  ℹ️  Tag '{tag_name}' already exists, using existing one")

        wait_for_enter()

        # FEATURE 2: PRIORITY LEVELS
        print_step(2, "Adding Tasks with Different Priorities 🎯")
        print("\n💡 NEW FEATURE: 4 Priority Levels")
        print("   🔴 URGENT - Critical, do immediately")
        print("   🟠 HIGH - Important, do today")
        print("   🟡 MEDIUM - Normal priority")
        print("   🟢 LOW - Can wait")

        print("\nCreating tasks with different priorities:")

        # Urgent task
        task1 = await add_task(
            db, DEMO_USER,
            title="Fix critical production bug",
            description="Database connection timeout",
            priority="urgent",
            tags=["work", "urgent"]
        )
        print(f"\n  🔴 URGENT: {task1['task']['title']}")
        print(f"     Tags: {', '.join(task1['task']['tags'])}")

        # High priority task with due date
        due_tomorrow = datetime.now() + timedelta(days=1)
        task2 = await add_task(
            db, DEMO_USER,
            title="Submit quarterly report",
            description="Q4 financial report for management",
            priority="high",
            due_date=due_tomorrow,
            tags=["work"]
        )
        print(f"\n  🟠 HIGH: {task2['task']['title']}")
        print(f"     Due: {task2['task']['due_date'][:10]}")
        print(f"     Tags: {', '.join(task2['task']['tags'])}")

        # Medium priority
        task3 = await add_task(
            db, DEMO_USER,
            title="Buy groceries",
            priority="medium",
            tags=["personal"]
        )
        print(f"\n  🟡 MEDIUM: {task3['task']['title']}")

        # Low priority
        task4 = await add_task(
            db, DEMO_USER,
            title="Read technical book",
            priority="low",
            tags=["personal"]
        )
        print(f"\n  🟢 LOW: {task4['task']['title']}")

        wait_for_enter()

        # FEATURE 3: LIST ALL TASKS
        print_step(3, "Listing All Tasks 📋")
        print("\n💡 See all your tasks with their priorities and tags")

        all_tasks = await list_tasks(db, DEMO_USER)
        print(f"\n📊 Total Tasks: {all_tasks['count']}\n")

        for i, task in enumerate(all_tasks['tasks'], 1):
            priority_emoji = {
                "urgent": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(task['priority'], "⚪")

            status = "✓" if task['completed'] else "○"
            tags_str = ", ".join(task.get('tags', []))

            print(f"  {status} {priority_emoji} [{task['priority'].upper()}] {task['title']}")
            if tags_str:
                print(f"     🏷️  {tags_str}")

        wait_for_enter()

        # FEATURE 4: FILTER BY PRIORITY
        print_step(4, "Filtering by Priority 🔍")
        print("\n💡 NEW FEATURE: Filter tasks by priority level")
        print("\nShowing only URGENT tasks:")

        urgent_tasks = await list_tasks(db, DEMO_USER, priority="urgent")
        print(f"\n🔴 Urgent Tasks ({urgent_tasks['count']}):\n")

        for task in urgent_tasks['tasks']:
            print(f"  • {task['title']}")
            if task.get('tags'):
                print(f"    Tags: {', '.join(task['tags'])}")

        wait_for_enter()

        # FEATURE 5: SEARCH
        print_step(5, "Smart Search 🔎")
        print("\n💡 NEW FEATURE: Search tasks by keyword")
        print("\nSearching for 'report':")

        search_results = await list_tasks(db, DEMO_USER, search="report")
        print(f"\n🔍 Found {search_results['count']} task(s):\n")

        for task in search_results['tasks']:
            print(f"  • {task['title']}")
            if task.get('description'):
                print(f"    📝 {task['description']}")

        wait_for_enter()

        # FEATURE 6: FILTER BY TAGS
        print_step(6, "Filtering by Tags 🏷️")
        print("\n💡 NEW FEATURE: Find all tasks with specific tags")
        print("\nShowing tasks tagged 'work':")

        work_tasks = await list_tasks(db, DEMO_USER, tags=["work"])
        print(f"\n💼 Work Tasks ({work_tasks['count']}):\n")

        for task in work_tasks['tasks']:
            priority_emoji = {
                "urgent": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(task['priority'], "⚪")
            print(f"  {priority_emoji} {task['title']}")

        wait_for_enter()

        # FEATURE 7: DYNAMIC SORTING
        print_step(7, "Dynamic Sorting 📊")
        print("\n💡 NEW FEATURE: Sort tasks by any field")
        print("\nSorting by PRIORITY (highest first):")

        sorted_tasks = await list_tasks(
            db, DEMO_USER,
            sort_by="priority",
            sort_order="desc"
        )

        print("\n📈 Tasks sorted by priority:\n")
        for task in sorted_tasks['tasks']:
            priority_emoji = {
                "urgent": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(task['priority'], "⚪")
            print(f"  {priority_emoji} [{task['priority'].upper():6}] {task['title']}")

        wait_for_enter()

        # FEATURE 8: UPDATE TASK
        print_step(8, "Updating Task Priority & Tags ✏️")
        print("\n💡 NEW FEATURE: Update any field including priority and tags")
        print(f"\nChanging '{task3['task']['title']}' to HIGH priority")
        print("Adding 'urgent' tag")

        updated = await update_task(
            db, DEMO_USER,
            task_id=task3['task']['id'],
            priority="high",
            tags=["personal", "urgent"]
        )

        print(f"\n✅ Updated successfully!")
        print(f"   Priority: MEDIUM → HIGH 🟠")
        print(f"   Tags: {', '.join(updated['task']['tags'])}")

        wait_for_enter()

        # FEATURE 9: TAG ANALYTICS
        print_step(9, "Tag Usage Analytics 📊")
        print("\n💡 NEW FEATURE: See how many tasks use each tag")

        all_tags = await list_tags(db, DEMO_USER)
        print(f"\n🏷️  Your Tags ({all_tags['count']}):\n")

        for tag in all_tags['tags']:
            bar = "█" * tag['usage_count']
            print(f"  {tag['name']:12} {tag['color']:8} [{tag['usage_count']} tasks] {bar}")

        wait_for_enter()

        # FEATURE 10: COMPLETE TASK
        print_step(10, "Completing Tasks ✓")
        print("\n💡 Mark tasks as done")
        print(f"\nCompleting: '{task4['task']['title']}'")

        completed = await complete_task(db, DEMO_USER, task4['task']['id'])
        print(f"\n✅ Task completed!")
        print(f"   Status: {'✓ Done' if completed['task']['completed'] else 'Pending'}")

        wait_for_enter()

        # SUMMARY
        print_header("🎊 DEMO COMPLETE!")
        print("\n✅ Features You Just Tried:\n")
        features = [
            "🏷️  Colorful tags for organization",
            "🎯 4-level priority system (Urgent/High/Medium/Low)",
            "📅 Due dates for deadlines",
            "🔍 Smart search by keywords",
            "🔎 Filter by priority level",
            "🏷️  Filter by tags",
            "📊 Dynamic sorting (by priority, date, etc.)",
            "✏️  Update tasks with new priority/tags",
            "📈 Tag usage analytics",
            "✓  Mark tasks complete",
        ]

        for i, feature in enumerate(features, 1):
            print(f"  {i:2}. {feature}")

        print("\n" + "="*70)
        print("  💪 All Phase 5 Features Working Perfectly!")
        print("="*70)

        print("\n🚀 Next Steps:")
        print("  1. Open browser: http://localhost:5173")
        print("  2. Login and try these features yourself")
        print("  3. Use natural language: 'Add high priority task'")
        print("\n📖 Full feature list: PHASE5_FEATURES.md")
        print("\n✨ Your basic todo app is now a professional task manager!")

if __name__ == "__main__":
    asyncio.run(main())
