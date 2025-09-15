"""
FastAPI Chatbot Backend with OpenAI Streaming
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, health
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Smart Chatbot API",
    description="A FastAPI backend with OpenAI streaming responses and memory-ready architecture",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
# Memory management is now handled automatically by AI tool calls

@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Smart Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
