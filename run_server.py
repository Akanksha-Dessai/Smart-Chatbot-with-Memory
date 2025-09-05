#!/usr/bin/env python3
"""
Server startup script for the Smart Chatbot Backend
"""

import uvicorn
import os
from app.config import settings

if __name__ == "__main__":
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = settings.debug
    
    print(f"Starting {settings.app_name} server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug mode: {reload}")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/api/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
