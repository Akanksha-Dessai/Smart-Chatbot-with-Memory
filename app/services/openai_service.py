"""
OpenAI service for handling chat completions with streaming
"""

import asyncio
from typing import AsyncGenerator, List, Dict, Any
import openai
from openai import AsyncOpenAI
from app.config import settings
from app.models.chat import StreamChunk
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI's Chat Completions API"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        self.system_prompt = settings.system_prompt
    
    async def stream_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        user_id: str
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream chat completion from OpenAI
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User identifier for logging and context
            
        Yields:
            StreamChunk: Chunks of the streaming response
        """
        try:
            # Prepare messages with system prompt
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            logger.info(f"Starting streaming chat completion for user {user_id}")
            
            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            # Stream the response
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield StreamChunk(content=content, done=False)
            
            # Send final done signal
            yield StreamChunk(content="", done=True)
            logger.info(f"Completed streaming chat completion for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in streaming chat completion for user {user_id}: {str(e)}")
            # Yield error message
            yield StreamChunk(content=f"Sorry, I encountered an error: {str(e)}", done=True)
    
    async def get_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        user_id: str
    ) -> str:
        """
        Get a single chat completion (non-streaming)
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User identifier for logging and context
            
        Returns:
            str: Complete response from OpenAI
        """
        try:
            # Prepare messages with system prompt
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            logger.info(f"Getting chat completion for user {user_id}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            
            content = response.choices[0].message.content
            logger.info(f"Completed chat completion for user {user_id}")
            return content
            
        except Exception as e:
            logger.error(f"Error in chat completion for user {user_id}: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt
        
        Args:
            new_prompt: New system prompt to use
        """
        self.system_prompt = new_prompt
        logger.info("System prompt updated")

# Global service instance
openai_service = OpenAIService()
