"""
OpenAI service for handling chat completions with streaming and tool calls for memory
"""

import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
from app.config import settings
from app.models.chat import StreamChunk
from app.services.mem0_service import mem0_service
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for interacting with OpenAI's Chat Completions API with memory tool calls"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature #creativity of the AI.
        self.max_tokens = settings.openai_max_tokens #maximum number of tokens to generate.
        self.system_prompt = settings.system_prompt
        self.mem0_service = mem0_service #mem0 service to add memory.
        
        # Define memory tools for OpenAI function calling
        self.memory_tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_memory",
                    "description": "Store important information or facts about the user in memory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The important information or fact to remember about the user"
                            },
                            "importance": {
                                "type": "number",
                                "description": "Importance score from 0.0 to 1.0 (0.5 is default)",
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata about the memory",
                                "properties": {
                                    "category": {"type": "string", "description": "Category of the memory (e.g., 'preference', 'fact', 'goal')"},
                                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the memory"}
                                }
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memories",
                    "description": "ALWAYS use this when user asks about themselves, their preferences, what they like, or when they ask for recipes of food they like. Use this before answering any personal questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant memories (e.g., 'name', 'food', 'like', 'preferences', 'favorite')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of memories to return (default: 5)",
                                "minimum": 1,
                                "maximum": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_memories",
                    "description": "Get all memories for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_memory",
                    "description": "Update an existing memory with new content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "The ID of the memory to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "New content for the memory"
                            },
                            "importance": {
                                "type": "number",
                                "description": "New importance score from 0.0 to 1.0 (0.5 is default)",
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "metadata": {
                                "type": "object",
                                "description": "New metadata for the memory",
                                "properties": {
                                    "category": {"type": "string", "description": "Category of the memory (e.g., 'preference', 'fact', 'goal')"},
                                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the memory"}
                                }
                            }
                        },
                        "required": ["memory_id", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_memory",
                    "description": "Delete a specific memory by its ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "The ID of the memory to delete"
                            }
                        },
                        "required": ["memory_id"]
                    }
                }
            }
        ]
    
    async def _execute_tool_call(self, tool_call, user_id: str) -> Dict[str, Any]:
        #tool_call is the tool call from OpenAI - the memory operation that ai wants to perform.
        #user_id is the user's id.
        """
        Execute a tool call for memory operations
        
        Args:
            tool_call: The tool call from OpenAI
            user_id: User identifier
            
        Returns:
            Dictionary with tool call result
        """
        try:
            function_name = tool_call.function.name

            #json.loads is used to parse the arguments from the tool call.
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"🔧 EXECUTING TOOL CALL: {function_name} for user {user_id}")
            logger.info(f"🔧 Tool arguments: {function_args}")
            
            if function_name == "add_memory":
                content = function_args.get("content", "")
                #content meaning - the content of the memory.

                importance = function_args.get("importance", 0.5)
                #importance meaning - how important is the memory.

                #metadata meaning - additional information about the memory.
                metadata = function_args.get("metadata", {})
                
                # Add memory using Mem0 service
                result = await self.mem0_service.add_memory(
                    user_id=user_id,
                    messages=[{"role": "user", "content": content}],
                    metadata={
                        "importance": importance,
                        "type": "important_fact", #important_fact meaning - the memory is important.
                        **metadata
                    }
                )
                
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": result,
                    "success": "error" not in result
                }
                
            elif function_name == "search_memories":
                query = function_args.get("query", "")
                limit = function_args.get("limit", 5)
                
                memories = await self.mem0_service.search_memories(
                    user_id=user_id,
                    query=query,
                    limit=limit
                )
                
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": memories,
                    "success": True
                }
                
            elif function_name == "get_all_memories":
                memories = await self.mem0_service.get_all_memories(user_id)
                
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": memories,
                    "success": True
                }
                
            elif function_name == "update_memory":
                memory_id = function_args.get("memory_id", "")
                content = function_args.get("content", "")
                importance = function_args.get("importance", 0.5)
                metadata = function_args.get("metadata", {})
                
                # Update memory using Mem0 service
                result = await self.mem0_service.update_memory(
                    memory_id=memory_id,
                    user_id=user_id,
                    content=content,
                    importance=importance,
                    metadata=metadata
                )
                
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": result,
                    "success": "error" not in result
                }
                
            elif function_name == "delete_memory":
                memory_id = function_args.get("memory_id", "")
                
                result = await self.mem0_service.delete_memory(
                    memory_id=memory_id,
                    user_id=user_id
                )
                
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": result,
                    "success": "error" not in result
                }
            
            else:
                return {
                    "tool_call_id": tool_call.id,
                    "function_name": function_name,
                    "result": {"error": f"Unknown function: {function_name}"},
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Error executing tool call {tool_call.function.name}: {str(e)}")
            return {
                "tool_call_id": tool_call.id,
                "function_name": tool_call.function.name,
                "result": {"error": str(e)},
                "success": False
            }
    
    async def stream_chat_completion(
        #handles the streaming of the chat completion with memory tool calls.
        self, 
        messages: List[Dict[str, str]],  #list of message dictionaries with 'role' and 'content'
        user_id: str,
        use_tools: bool = True   #whether to enable memory tool calls.
    ) -> AsyncGenerator[StreamChunk, None]:  
    #returns an async generator that yields StreamChunk objects - chunks of the streaming response.
        """
        Stream chat completion from OpenAI with optional tool calls for memory
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User identifier for logging and context
            use_tools: Whether to enable memory tool calls
            
        Yields:
            StreamChunk: Chunks of the streaming response
        """
        try:
            # Prepare messages with enhanced system prompt
            system_prompt = self.get_enhanced_system_prompt() if use_tools else self.system_prompt

            #if use_tools is true, then add the enhanced system prompt with memory instructions to the messages.
            #if use_tools is false, then add the basic system prompt without memory instructions to the messages.

            #system_prompt is the prompt text from AI.

            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            logger.info(f"🚀 Starting streaming chat completion for user {user_id} (tools: {use_tools})")
            logger.info(f"🔧 Available tools: {[tool['function']['name'] for tool in self.memory_tools]}")
            logger.info(f"💬 User message: {messages[-1]['content'] if messages else 'No message'}")
            
            # Creates request parameters for the OpenAI API call.
            completion_kwargs = {     #completion_kwargs is the request parameters for the OpenAI API call.
                "model": self.model,    #model is the model to use for the chat completion.
                "messages": full_messages,    #complete messages history.
                "temperature": self.temperature,    #creativity of the AI.
                "max_tokens": self.max_tokens,   #maximum number of tokens to generate.
                "stream": True    #Enable Streaming responses.
            }
            
            if use_tools:
                completion_kwargs["tools"] = self.memory_tools
                completion_kwargs["tool_choice"] = "auto"
            
            stream = await self.client.chat.completions.create(**completion_kwargs)
            
            # Track tool calls for execution
            tool_calls_to_execute = []
            current_tool_call = None
            
            # Stream the response
            async for chunk in stream: 
                #loops through each chunk of the response.

                choice = chunk.choices[0] #the first choice from the chunk.
                delta = choice.delta   #the changes in the chunk
                
                # Handle content streaming
                #checks if the chunk contains text content.
                if delta.content is not None:  
                    content = delta.content   #delta.content is the text.
                     #the actual text response.
                    yield StreamChunk(content=content, done=False) #yields the chunk.
                
                # Handle tool calls
                #Detects when the AI wants to use a tool.
                if delta.tool_calls:    #List of the tool calls from the chunk.
                    logger.info(f"🔧 DETECTED TOOL CALLS: {len(delta.tool_calls)} tool calls")
                    
                    for tool_call_delta in delta.tool_calls: 
                          #tool_call_delta is the each tool call from the chunk.
                        
                        if tool_call_delta.index is not None: 
                             #the index of the tool call.
                            
                            # New tool call
                            #like checks if we need to expand the array as extends the array with none values.
                            if tool_call_delta.index >= len(tool_calls_to_execute):
                                tool_calls_to_execute.extend([None] * (tool_call_delta.index + 1 - len(tool_calls_to_execute)))
                            
                            #checks if the tool call is not seen before like new tool call.
                            #first time seen in this call create new.
                            if tool_calls_to_execute[tool_call_delta.index] is None:
                                tool_calls_to_execute[tool_call_delta.index] = {
                                    "id": tool_call_delta.id,  #unique id for the tool call.
                                    "type": tool_call_delta.type,  #type of the tool call.
                                    "function": {
                                        "name": tool_call_delta.function.name,  #name of the tool call.
                                        "arguments": tool_call_delta.function.arguments or ""  #arguments of the tool call.
                                    }
                                }
                            else:
                                # Append to existing arguments
                                #same call called then appends directly without the loss of previous chunk call.
                                #checks where tool call arguments come in multiple chunks.
                                tool_calls_to_execute[tool_call_delta.index]["function"]["arguments"] += tool_call_delta.function.arguments or ""
                
                # Check if this is the final chunk
                if choice.finish_reason is not None:
                    if choice.finish_reason == "tool_calls" and tool_calls_to_execute:
                        logger.info(f"🔧 PROCESSING {len(tool_calls_to_execute)} TOOL CALLS")
                        # First, add the assistant's message with tool calls
                        assistant_message = {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": []
                        }
                        
                        for tool_call_data in tool_calls_to_execute:
                            #list of tool call in the message is tool_call_to_execute.
                            if tool_call_data:
                                #each complete tool call from the array
                                assistant_message["tool_calls"].append({
                                    "id": tool_call_data["id"],
                                    "type": tool_call_data["type"],
                                    "function": tool_call_data["function"]
                                })
                        
                        full_messages.append(assistant_message)
                        
                        # Execute tool calls
                        for tool_call_data in tool_calls_to_execute:
                            if tool_call_data:
                                # Create a mock tool call object
                                #is needed because execute_tool_call expects a tool call object.
                                class MockToolCall:
                                    def __init__(self, data):
                                        self.id = data["id"]
                                        self.type = data["type"]
                                        self.function = type('obj', (object,), data["function"])()
                                
                                tool_call = MockToolCall(tool_call_data)
                                #converts dictionary to object with attributes.

                                tool_result = await self._execute_tool_call(tool_call, user_id)

                                
                                # Add tool result to messages to the conervsation histroy
                                full_messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(tool_result["result"]) #converts dictionary to json string.
                                })
                        
                        # Make another completion call with tool results
                        completion_kwargs["messages"] = full_messages
                        completion_kwargs["tools"] = None  
                    # Don't use tools in follow-up as ir prevents the tool call from being executed again infinitely.
                        completion_kwargs["tool_choice"] = None
                        
                        #streaming response with memory context
                        follow_up_stream = await self.client.chat.completions.create(**completion_kwargs)
                        
                        # Stream the follow-up response with memory context
                        #loops through each chunk of the response.
                        async for follow_up_chunk in follow_up_stream:
                            if follow_up_chunk.choices[0].delta.content is not None:
                                content = follow_up_chunk.choices[0].delta.content
                                #content is the actual text response.
                                yield StreamChunk(content=content, done=False)
                    
                    # Send final done signal to frontend the completion
                    yield StreamChunk(content="", done=True)
                    logger.info(f"Completed streaming chat completion for user {user_id}")
                    break
            
        except Exception as e:
            logger.error(f"Error in streaming chat completion for user {user_id}: {str(e)}")
            # Yield error message
            yield StreamChunk(content=f"Sorry, I encountered an error: {str(e)}", done=True)
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt
        
        Args:
            new_prompt: New system prompt to use
        """
        self.system_prompt = new_prompt
        logger.info("System prompt updated")
    
    def get_enhanced_system_prompt(self) -> str:
        """
        Get the enhanced system prompt with memory instructions
        
        Returns:
            str: Enhanced system prompt
        """
        memory_instructions = """
CRITICAL: You have memory tools and MUST use them:

1. When user shares personal info (name, preferences, facts) → IMMEDIATELY call add_memory()
2. When user asks about themselves → IMMEDIATELY call search_memories() 
3. When user asks "what do you remember" → IMMEDIATELY call get_all_memories()
4. When user asks for recipes of "food they like" → IMMEDIATELY call search_memories() to find their food preferences
5. When user corrects or updates information → IMMEDIATELY call update_memory() with the memory_id and new content
6. When user wants to delete information → IMMEDIATELY call delete_memory() with the memory_id

EXAMPLES:
- User: "My name is John" → Call add_memory() with content "User's name is John"
- User: "What is my name?" → Call search_memories() with query "name"
- User: "What do you remember?" → Call get_all_memories()
- User: "Give me recipe of food I like" → Call search_memories() with query "food" or "like"
- User: "Actually, my name is John Smith" → Call update_memory() with memory_id and content "User's name is John Smith"
- User: "Forget that I like pizza" → Call delete_memory() with memory_id of pizza memory

IMPORTANT: Always search memories when user asks about recipes, preferences, or anything personal. Use the stored information to provide personalized responses.
"""
        return self.system_prompt + memory_instructions

# Global service instance
openai_service = OpenAIService()
