"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add parent directory to path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app

# Export the FastAPI app as 'app' for Vercel
__all__ = ['app']
