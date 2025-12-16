"""Debug script to check what config values are loaded"""
import sys
import os

# Set PYTHONPATH
sys.path.insert(0, '/home/umair/todo-chatbot')

# Force reload of config
import importlib
if 'backend.config' in sys.modules:
    del sys.modules['backend.config']

from backend.config import get_settings

settings = get_settings()

print("=" * 60)
print("🔍 Backend Configuration Debug")
print("=" * 60)
print(f"\nCurrent Directory: {os.getcwd()}")
print(f"\nBETTER_AUTH_SECRET: {settings.BETTER_AUTH_SECRET}")
print(f"BETTER_AUTH_ISSUER: {settings.BETTER_AUTH_ISSUER}")
print(f"\nSecret Length: {len(settings.BETTER_AUTH_SECRET)}")
print(f"Secret (first 10 chars): {settings.BETTER_AUTH_SECRET[:10]}...")
print(f"Secret (last 10 chars): ...{settings.BETTER_AUTH_SECRET[-10:]}")
print("\n" + "=" * 60)
