"""
Configuration settings for the chatbot application
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000
    
    # Mem0 Configuration
    mem0_api_key: str
    mem0_model: str = "gpt-3.5-turbo"
    mem0_embedding_model: str = "text-embedding-3-small"
    
    # System Prompt Configuration
    system_prompt: str = """You are a helpful AI assistant with memory capabilities. You provide clear, concise, and accurate responses to user questions. 
    You maintain a friendly and professional tone while being informative and helpful. You can remember important details about users and their preferences."""
    
    # Application Configuration
    app_name: str = "Smart Chatbot"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
