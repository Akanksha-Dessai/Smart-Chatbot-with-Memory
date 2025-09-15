"""
Chat routes for handling user conversations with streaming responses
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import logging

from app.models.chat import ChatRequest, StreamChunk
from app.services.openai_service import openai_service
# Memory service no longer needed - handled by OpenAI tool calls

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
        
        # Prepare messages for OpenAI with tool calls
        # The OpenAI service will now handle memory operations through tool calls
        # This below will contain the conversation history.
        #request.message is the actual user's message.

        #system - instruction to the AI
        #user - the user's message
        #assistant - the AI's response
        
        messages = [{"role": "user", "content": request.message}]
        
        # Create an async generator function that will generate streaming data.
        async def generate_response() -> AsyncGenerator[str, None]:
            """Generate streaming response chunks"""
            full_response = ""
            
            #full_response empty string to track the complete response.

            try:
                #OpenAI Service Call with Memory Tools
                async for chunk in openai_service.stream_chat_completion(messages, request.user_id):
                   #messages - the users messages in openai format. 
                   #request.user_id - the user's id.
                   #chunk - each piece of the AI response.
                   #chunk.done - boolean to check if the response is complete. like true or false.
                    if chunk.done: 
                        # Send final chunk like in server sent events.
                        yield f"data: {chunk.model_dump_json()}\n\n"
                    else:
                        full_response += chunk.content #complete response
                        yield f"data: {chunk.model_dump_json()}\n\n"

                        #chunk.content - the actual response.
                        #model_dump_json() - convert the chunk to a json string.
                
                # Send completion signal to tell streaming is complete.
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

