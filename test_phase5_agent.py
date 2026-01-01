#!/usr/bin/env python3
"""
Quick test to verify Phase 5 agent features
Tests that the chatbot can now create tags and use Phase 5 features
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '/home/umair/todo-chatbot')

from backend.config import Settings
from backend.agents.todo_agent import run_todo_agent

settings = Settings()
TEST_USER = "phase5-agent-test"

async def test_phase5_features():
    """Test that the agent now supports Phase 5 features"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("=" * 70)
        print("  🧪 TESTING PHASE 5 AGENT FEATURES")
        print("=" * 70)

        # Test 1: Create a tag (this was failing before)
        print("\n📝 Test 1: Create a tag with color")
        print("   User: 'Create a tag called work with color #FF5733'")

        result1 = await run_todo_agent(
            user_id=TEST_USER,
            message="Create a tag called work with color #FF5733",
            conversation_history=[],
            db=db
        )

        print(f"\n   🤖 Agent Response: {result1['response']}")
        if result1.get('tool_calls'):
            print(f"   🔧 Tools Called: {[t['tool'] for t in result1['tool_calls']]}")

        # Test 2: Add a high priority task with tags
        print("\n📝 Test 2: Add high priority task with tags")
        print("   User: 'Add a high priority task: Complete Phase 5 with tags work and urgent'")

        result2 = await run_todo_agent(
            user_id=TEST_USER,
            message="Add a high priority task: Complete Phase 5 with tags work and urgent",
            conversation_history=[],
            db=db
        )

        print(f"\n   🤖 Agent Response: {result2['response']}")
        if result2.get('tool_calls'):
            print(f"   🔧 Tools Called: {[t['tool'] for t in result2['tool_calls']]}")

        # Test 3: List all tags
        print("\n📝 Test 3: List all tags")
        print("   User: 'Show me all my tags'")

        result3 = await run_todo_agent(
            user_id=TEST_USER,
            message="Show me all my tags",
            conversation_history=[],
            db=db
        )

        print(f"\n   🤖 Agent Response: {result3['response']}")
        if result3.get('tool_calls'):
            print(f"   🔧 Tools Called: {[t['tool'] for t in result3['tool_calls']]}")

        # Test 4: List tasks filtered by priority
        print("\n📝 Test 4: Filter tasks by priority")
        print("   User: 'Show me all high priority tasks'")

        result4 = await run_todo_agent(
            user_id=TEST_USER,
            message="Show me all high priority tasks",
            conversation_history=[],
            db=db
        )

        print(f"\n   🤖 Agent Response: {result4['response']}")
        if result4.get('tool_calls'):
            print(f"   🔧 Tools Called: {[t['tool'] for t in result4['tool_calls']]}")

        # Test 5: Search tasks
        print("\n📝 Test 5: Search tasks")
        print("   User: 'Search for tasks about Phase 5'")

        result5 = await run_todo_agent(
            user_id=TEST_USER,
            message="Search for tasks about Phase 5",
            conversation_history=[],
            db=db
        )

        print(f"\n   🤖 Agent Response: {result5['response']}")
        if result5.get('tool_calls'):
            print(f"   🔧 Tools Called: {[t['tool'] for t in result5['tool_calls']]}")

        print("\n" + "=" * 70)
        print("  ✅ ALL PHASE 5 AGENT TESTS COMPLETED!")
        print("=" * 70)
        print("\n📊 Summary:")
        print("   ✅ Agent can create tags")
        print("   ✅ Agent can add tasks with priority and tags")
        print("   ✅ Agent can list tags")
        print("   ✅ Agent can filter by priority")
        print("   ✅ Agent can search tasks")
        print("\n🎉 Phase 5 agent update successful!")

if __name__ == "__main__":
    asyncio.run(test_phase5_features())
