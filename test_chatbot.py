"""
Test chatbot with Phase 5 features via API
"""
import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"

# First, you need to login to get a token
def login():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "aftabumair766@gmail.com",
            "password": "your-password-here"  # Replace with your actual password
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

# Send message to chatbot
def chat(token, message):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={"message": message}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Chat failed: {response.text}")
        return None

# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("CHATBOT TEST - Phase 5 Features")
    print("=" * 60)

    # Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Please check your credentials.")
        exit(1)
    print("✅ Login successful!")

    # Test Phase 5 features
    test_messages = [
        "Add a high priority task: Complete annual report by Friday",
        "Add a task: Buy groceries with tags personal and urgent",
        "Show me all high priority tasks",
        "List all my tasks sorted by priority",
        "Search for tasks containing 'report'",
        "Create a tag called 'work' with color #FF5733",
        "Show me all tasks with tag 'urgent'",
        "Update task 1 to urgent priority",
        "List all my tags",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        result = chat(token, message)
        if result:
            print(f"   Bot: {result.get('response', 'No response')}")
        print("-" * 60)

print("\n✅ All chatbot features tested!")
