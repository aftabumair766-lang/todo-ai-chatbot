"""
Vercel Entry Point for FastAPI Application
"""
from backend.main import app

# This is the ASGI application that Vercel will use
# Vercel automatically detects this file in /api/index.py
