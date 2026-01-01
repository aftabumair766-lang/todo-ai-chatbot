#!/usr/bin/env python3
"""
Interactive chatbot tester - Use Phase 5 features
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def main():
    print("=" * 60)
    print("TODO CHATBOT - Phase 5 Features")
    print("=" * 60)

    # Login
    print("\nLogin credentials from .env file:")
    email = "aftabumair766@gmail.com"
    password = input("Enter your password: ").strip()

    print("\nLogging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

    token = response.json()["access_token"]
    print("✅ Login successful!")
    print("\n" + "=" * 60)
    print("Chat with your AI assistant (type 'exit' to quit)")
    print("=" * 60)

    # Example commands
    print("\nTry these Phase 5 commands:")
    print("  • Add a high priority task: Finish report by Friday")
    print("  • Show me all high priority tasks")
    print("  • Create a tag called 'work' with color #FF5733")
    print("  • List tasks sorted by priority")
    print("  • Search for tasks containing 'report'")
    print()

    # Chat loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            # Send message to chatbot
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{BASE_URL}/api/chat",
                headers=headers,
                json={"message": user_input}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"\nBot: {result.get('response', 'No response')}")
            else:
                print(f"\n❌ Error: {response.text}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
