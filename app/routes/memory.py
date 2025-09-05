"""
Memory management routes for Mem0 integration
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
import logging
from datetime import datetime
from pydantic import BaseModel

from app.services.memory import memory_service
from app.services.mem0_service import mem0_service

logger = logging.getLogger(__name__)
router = APIRouter()

class MemoryRequest(BaseModel):
    memory_text: str
    importance: float = 0.5
    metadata: Optional[dict] = None

@router.get("/memories/stats")
async def get_memory_stats():
    """
    Get memory system statistics
    
    Returns:
        Memory statistics
    """
    try:
        local_stats = memory_service.get_memory_stats()
        mem0_stats = await mem0_service.get_memory_stats()
        
        return {
            "local_stats": local_stats,
            "mem0_stats": mem0_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/memories/{user_id}")
async def get_user_memories(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """
    Get memories for a user from Mem0
    
    Args:
        user_id: User identifier
        limit: Maximum number of memories to return
        search: Optional search query to filter memories
        
    Returns:
        List of user memories
    """
    try:
        if search:
            memories = await memory_service.get_relevant_memories(user_id, search, limit)
        else:
            memories = await memory_service.get_all_memories(user_id)
            memories = memories[:limit]  # Limit results
        
        return {
            "user_id": user_id,
            "memories": memories,
            "count": len(memories),
            "search_query": search
        }
    except Exception as e:
        logger.error(f"Error retrieving memories for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/memories/{user_id}")
async def add_memory(user_id: str, request: MemoryRequest):
    """
    Add a new memory for a user (like JavaScript examples)
    
    Args:
        user_id: User identifier
        request: MemoryRequest with memory_text, importance, and metadata
        
    Returns:
        Memory creation result
    """
    try:
        result = await memory_service.add_important_fact(
            user_id, request.memory_text, request.importance, request.metadata
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "memory_text": request.memory_text,
            "importance": request.importance,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding memory for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """
    Delete a specific memory
    
    Args:
        user_id: User identifier
        memory_id: Memory identifier
        
    Returns:
        Deletion result
    """
    try:
        result = await memory_service.delete_memory(memory_id, user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "memory_id": memory_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory {memory_id} for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/memories/{user_id}")
async def clear_user_memories(user_id: str):
    """
    Clear all memories for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Clearing result
    """
    try:
        result = await memory_service.clear_user_memories(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing memories for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/memories/search/{user_id}")
async def search_memories(
    user_id: str,
    query: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for relevant memories for a user
    
    Args:
        user_id: User identifier
        query: Search query
        limit: Maximum number of results
        
    Returns:
        Search results
    """
    try:
        memories = await memory_service.get_relevant_memories(user_id, query, limit)
        
        return {
            "user_id": user_id,
            "query": query,
            "memories": memories,
            "count": len(memories),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching memories for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/memories/{user_id}/context")
async def get_memory_context(
    user_id: str,
    message: str,
    max_recent: int = Query(5, ge=1, le=20),
    max_memories: int = Query(3, ge=1, le=10)
):
    """
    Get enhanced context for a user's message
    
    Args:
        user_id: User identifier
        message: Current message to get context for
        max_recent: Maximum recent messages to include
        max_memories: Maximum relevant memories to include
        
    Returns:
        Enhanced context information
    """
    try:
        enhanced_context = await memory_service.get_enhanced_context(
            user_id, message, max_recent, max_memories
        )
        
        return {
            "user_id": user_id,
            "message": message,
            "context": enhanced_context,
            "context_length": len(enhanced_context),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting memory context for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")