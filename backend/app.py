"""Hugging Face Spaces Entry Point.

This file serves as the main entry point (app.py) when deploying the FastAPI backend 
directly to a Hugging Face Space.
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Hugging Face Spaces uses the PORT environment variable (defaulting to 7860)
    port = int(os.environ.get("PORT", 7860))
    
    print(f"🚀 Launching FastAPI backend for Hugging Face Spaces on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
