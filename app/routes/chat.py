"""
Chat routes for handling user conversations with streaming responses
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import logging
from datetime import datetime

from app.models.chat import ChatRequest, StreamChunk
from app.services.openai_service import openai_service
from app.services.memory import memory_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat")
async def chat_stream(request: ChatRequest):
    """
    Chat endpoint with streaming OpenAI responses
    
    Args:
        request: ChatRequest containing user_id and message
        
    Returns:
        StreamingResponse: Server-sent events with chat response chunks
    """
    try:
        logger.info(f"Received chat request from user {request.user_id}")
        
        # Get enhanced context with Mem0 memories
        enhanced_context = await memory_service.get_enhanced_context(
            request.user_id, 
            request.message,
            max_recent_messages=5,
            max_relevant_memories=3
        )
        
        # Add current user message
        messages = enhanced_context + [{"role": "user", "content": request.message}]
        
        # Create streaming response generator
        async def generate_response() -> AsyncGenerator[str, None]:
            """Generate streaming response chunks"""
            full_response = ""
            
            try:
                # Stream OpenAI response
                async for chunk in openai_service.stream_chat_completion(messages, request.user_id):
                    if chunk.done:
                        # Store conversation in memory
                        if full_response.strip():
                            memory_service.add_conversation(
                                request.user_id,
                                request.message,
                                full_response
                            )
                        
                        # Send final chunk
                        yield f"data: {chunk.model_dump_json()}\n\n"
                    else:
                        full_response += chunk.content
                        yield f"data: {chunk.model_dump_json()}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response for user {request.user_id}: {str(e)}")
                error_chunk = StreamChunk(content=f"Error: {str(e)}", done=True)
                yield f"data: {error_chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request for user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """
    Simple chat endpoint without streaming (for testing)
    
    Args:
        request: ChatRequest containing user_id and message
        
    Returns:
        dict: Complete chat response
    """
    try:
        logger.info(f"Received simple chat request from user {request.user_id}")
        
        # Get enhanced context with Mem0 memories
        enhanced_context = await memory_service.get_enhanced_context(
            request.user_id, 
            request.message,
            max_recent_messages=5,
            max_relevant_memories=3
        )
        
        # Add current user message
        messages = enhanced_context + [{"role": "user", "content": request.message}]
        
        # Get complete response
        response = await openai_service.get_chat_completion(messages, request.user_id)
        
        # Store conversation in memory
        memory_service.add_conversation(request.user_id, request.message, response)
        
        return {
            "user_id": request.user_id,
            "message": request.message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing simple chat request for user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """
    Get chat history for a user
    
    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return
        
    Returns:
        dict: User's chat history
    """
    try:
        history = memory_service.get_conversation_history(user_id, limit=limit)
        return {
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/chat/history/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear chat history for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: Confirmation message
    """
    try:
        memory_service.clear_user_memory(user_id)
        return {"message": f"Chat history cleared for user {user_id}"}
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
