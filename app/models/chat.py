"""
Pydantic models for chat-related requests and responses
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    user_id: str = Field(..., description="Unique identifier for the user", min_length=1)
    message: str = Field(..., description="User's message to the chatbot", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Hello, how are you today?"
            }
        }

class ChatResponse(BaseModel):
    """Response model for chat endpoint (non-streaming)"""
    user_id: str
    message: str
    response: str
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Hello, how are you today?",
                "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class StreamChunk(BaseModel):
    """Model for streaming response chunks"""
    content: str
    done: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello! I'm doing well",
                "done": False
            }
        }

class MemoryEntry(BaseModel):
    """Model for memory entries (placeholder for future Mem0 integration)"""
    user_id: str
    content: str
    timestamp: str
    importance: Optional[float] = None
