"""
Dynamic Memory Service - Like ChatGPT
No explicit instructions, works automatically based on context
"""

import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any
import openai
from openai import AsyncOpenAI
from app.config import settings
from app.models.chat import StreamChunk
from app.services.mem0_service import mem0_service
import logging

logger = logging.getLogger(__name__)

class DynamicMemoryService:
    """Dynamic memory service that works like ChatGPT - automatically"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        
        # Simple memory tool - like ChatGPT
        self.memory_tool = {
            "type": "function",
            "function": {
                "name": "manage_memory",
                "description": "Store or retrieve user information. Use 'store' to save important details about the user, 'retrieve' to get user information when needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["store", "retrieve"],
                            "description": "Action to perform: 'store' to save information, 'retrieve' to get information"
                        },
                        "key": {
                            "type": "string",
                            "description": "Key identifier for the information (e.g., 'name', 'food_preference', 'hobby')"
                        },
                        "value": {
                            "type": "string",
                            "description": "Information to store (required for 'store' action)"
                        }
                    },
                    "required": ["action", "key"]
                }
            }
        }
    
    async def _execute_memory_action(self, action: str, key: str, value: str = None, user_id: str = None) -> str:
        """Execute memory action"""
        try:
            if action == "store" and value:
                # Store information
                result = await mem0_service.add_memory(
                    user_id=user_id,
                    messages=[{"role": "user", "content": f"{key}: {value}"}],
                    metadata={"key": key, "type": "user_info", "importance": 0.8}
                )
                return f"Stored {key}: {value}"
                
            elif action == "retrieve":
                # Retrieve information
                memories = await mem0_service.search_memories(user_id, key, limit=3)
                if memories:
                    info = []
                    for memory in memories:
                        if 'memory' in memory:
                            info.append(memory['memory'])
                    return f"Retrieved {key}: {'; '.join(info)}"
                else:
                    return f"No information found for {key}"
            
            return f"Invalid action: {action}"
            
        except Exception as e:
            logger.error(f"Error in memory action {action}: {e}")
            return f"Error: {str(e)}"
    
    async def stream_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        user_id: str
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Dynamic chat completion - works like ChatGPT automatically
        """
        try:
            logger.info(f"🚀 Dynamic chat for user {user_id}")
            
            # FIRST CALL - Let AI decide if it needs memory
            first_completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=[self.memory_tool],
                tool_choice="auto",  # AI decides automatically
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            first_message = first_completion.choices[0].message
            
            # Check if AI wants to use memory
            if first_message.tool_calls:
                logger.info(f"🧠 AI decided to use memory: {len(first_message.tool_calls)} calls")
                
                # Execute memory actions
                tool_responses = []
                for tool_call in first_message.tool_calls:
                    function_name = tool_call.function.name
                    if function_name == "manage_memory":
                        arguments = json.loads(tool_call.function.arguments)
                        action = arguments.get("action")
                        key = arguments.get("key")
                        value = arguments.get("value")
                        
                        logger.info(f"🧠 Memory action: {action} {key} = {value}")
                        
                        # Execute memory action
                        result = await self._execute_memory_action(action, key, value, user_id)
                        
                        tool_responses.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })
                
                # SECOND CALL - AI gets memory results and responds
                second_messages = messages + [
                    {"role": "assistant", "content": None, "tool_calls": first_message.tool_calls}
                ] + tool_responses
                
                # Stream the final response
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=second_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                
                # Stream the response
                async for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        yield StreamChunk(content=content, done=False)
                
            else:
                # No memory needed - stream direct response
                logger.info("💬 No memory needed - direct response")
                yield StreamChunk(content=first_message.content or "", done=False)
            
            # Send final done signal
            yield StreamChunk(content="", done=True)
            logger.info(f"✅ Completed dynamic chat for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in dynamic chat for user {user_id}: {str(e)}")
            yield StreamChunk(content=f"Sorry, I encountered an error: {str(e)}", done=True)

# Global dynamic service instance
dynamic_memory_service = DynamicMemoryService()
