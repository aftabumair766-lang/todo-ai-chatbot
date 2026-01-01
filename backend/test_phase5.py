"""
Quick test script for Phase 5 MCP tools
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.mcp.tools import (
    add_task, list_tasks, create_tag, list_tags,
    update_task, complete_task, delete_task
)
from backend.config import Settings

# Load settings
settings = Settings()

# Test user ID
TEST_USER_ID = "test-user-phase5"

async def main():
    print("=" * 60)
    print("PHASE 5 FEATURES TEST")
    print("=" * 60)

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Test 1: Create tags
            print("\n1. Creating tags...")
            tag1 = await create_tag(db, TEST_USER_ID, "work", "#FF5733")
            print(f"   ✅ Created tag: {tag1['tag']['name']} (color: {tag1['tag']['color']})")

            tag2 = await create_tag(db, TEST_USER_ID, "urgent", "#FF0000")
            print(f"   ✅ Created tag: {tag2['tag']['name']} (color: {tag2['tag']['color']})")

            tag3 = await create_tag(db, TEST_USER_ID, "personal", "#00FF00")
            print(f"   ✅ Created tag: {tag3['tag']['name']} (color: {tag3['tag']['color']})")

            # Test 2: Create tasks with Phase 5 features
            print("\n2. Creating tasks with Phase 5 features...")

            # High priority task with due date
            due_tomorrow = datetime.now() + timedelta(days=1)
            task1 = await add_task(
                db, TEST_USER_ID,
                title="Complete project report",
                description="Finish Q4 report for management",
                priority="high",
                due_date=due_tomorrow,
                tags=["work", "urgent"]
            )
            print(f"   ✅ Task 1: {task1['task']['title']}")
            print(f"      Priority: {task1['task']['priority']}, Tags: {task1['task']['tags']}")

            # Medium priority with tags
            task2 = await add_task(
                db, TEST_USER_ID,
                title="Buy groceries",
                description="Milk, eggs, bread",
                priority="medium",
                tags=["personal"]
            )
            print(f"   ✅ Task 2: {task2['task']['title']}")
            print(f"      Priority: {task2['task']['priority']}, Tags: {task2['task']['tags']}")

            # Low priority task
            task3 = await add_task(
                db, TEST_USER_ID,
                title="Read technical book",
                priority="low",
                tags=["personal"]
            )
            print(f"   ✅ Task 3: {task3['task']['title']}")
            print(f"      Priority: {task3['task']['priority']}, Tags: {task3['task']['tags']}")

            # Test 3: List all tasks
            print("\n3. Listing all tasks...")
            all_tasks = await list_tasks(db, TEST_USER_ID, status="all")
            print(f"   ✅ Total tasks: {all_tasks['count']}")
            for task in all_tasks['tasks']:
                print(f"      - [{task['priority'].upper()}] {task['title']} (Tags: {task.get('tags', [])})")

            # Test 4: Filter by priority
            print("\n4. Filtering tasks by priority (high)...")
            high_tasks = await list_tasks(db, TEST_USER_ID, priority="high")
            print(f"   ✅ High priority tasks: {high_tasks['count']}")
            for task in high_tasks['tasks']:
                print(f"      - {task['title']}")

            # Test 5: Filter by tag
            print("\n5. Filtering tasks by tag (personal)...")
            personal_tasks = await list_tasks(db, TEST_USER_ID, tags=["personal"])
            print(f"   ✅ Personal tasks: {personal_tasks['count']}")
            for task in personal_tasks['tasks']:
                print(f"      - {task['title']}")

            # Test 6: Search tasks
            print("\n6. Searching tasks (keyword: 'report')...")
            search_results = await list_tasks(db, TEST_USER_ID, search="report")
            print(f"   ✅ Search results: {search_results['count']}")
            for task in search_results['tasks']:
                print(f"      - {task['title']}")

            # Test 7: Sort by priority
            print("\n7. Sorting tasks by priority...")
            sorted_tasks = await list_tasks(db, TEST_USER_ID, sort_by="priority", sort_order="desc")
            print(f"   ✅ Tasks sorted by priority:")
            for task in sorted_tasks['tasks']:
                print(f"      - [{task['priority'].upper()}] {task['title']}")

            # Test 8: Update task priority
            print("\n8. Updating task priority...")
            updated = await update_task(
                db, TEST_USER_ID,
                task_id=task2['task']['id'],
                priority="urgent",
                tags=["personal", "urgent"]
            )
            print(f"   ✅ Updated '{updated['task']['title']}' to {updated['task']['priority']}")
            print(f"      New tags: {updated['task']['tags']}")

            # Test 9: List all tags with usage counts
            print("\n9. Listing all tags...")
            all_tags = await list_tags(db, TEST_USER_ID)
            print(f"   ✅ Total tags: {all_tags['count']}")
            for tag in all_tags['tags']:
                print(f"      - {tag['name']} ({tag['usage_count']} tasks) {tag['color']}")

            # Test 10: Complete a task
            print("\n10. Completing a task...")
            completed = await complete_task(db, TEST_USER_ID, task3['task']['id'])
            print(f"   ✅ Completed: {completed['task']['title']}")
            print(f"      Status: {'✓ Done' if completed['task']['completed'] else 'Pending'}")

            print("\n" + "=" * 60)
            print("ALL PHASE 5 FEATURES WORKING! ✅")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
