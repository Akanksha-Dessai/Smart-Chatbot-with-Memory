"""
Pydantic models for chat-related requests and responses
"""

from typing import Optional, List   #import for optional and list fields
from pydantic import BaseModel, Field  #python library for data validation and parsing

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    user_id: str = Field(..., description="Unique identifier for the user", min_length=1)
    message: str = Field(..., description="User's message to the chatbot", min_length=1)
    
    #The class Config is a configuration class inside 
    #Pydantic models that tells Pydantic how to behave. 
    #It's like giving instructions to Pydantic about how to handle your data.
    #better for API documentation and validation.

    #pydantic meaning - python data validation and parsing library.
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Hello, how are you today?"
            }
        }

class StreamChunk(BaseModel):
    """Model for streaming response chunks"""
    content: str    #the actual text response.
    done: bool = False  #so tells like whether the response is final or more coming.
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello! I'm doing well",
                "done": False
            }
        }

class MemoryEntry(BaseModel):
    """Model for memory entries (placeholder for future Mem0 integration)"""
    user_id: str   #the user's id.
    content: str   #the content of the memory.
    timestamp: str   #the timestamp of the memory when it
    importance: Optional[float] = None   #the importance of the memory.
