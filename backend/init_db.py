"""
Initialize database - Quick setup for development
"""
import asyncio
from backend.db.session import init_db

async def main():
    print("🗄️  Creating database tables...")
    await init_db()
    print("✅ Database initialized!")

if __name__ == "__main__":
    asyncio.run(main())
