"""

Mem0 service for intelligent memory management using proper Mem0 API format
Based on the JavaScript examples in the MEM0 folder
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging
from mem0 import MemoryClient
from app.config import settings

logger = logging.getLogger(__name__)

class Mem0Service:
    """Service for managing memories using Mem0 API client"""
    
    def __init__(self):
        """Initialize Mem0 client with API key"""
        try:
            # Use MemoryClient with API key like the JavaScript examples
            self.client = MemoryClient(api_key=settings.mem0_api_key)
            logger.info("Mem0 service initialized successfully with API key")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0 service: {str(e)}")
            self.client = None
    
    async def add_memory(
        self, 
        user_id: str, 
        messages: List[Dict[str, str]], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add memories from conversation messages (like JavaScript examples)
        
        Args:
            user_id: User identifier
            messages: List of message dictionaries with 'role' and 'content'
            metadata: Optional metadata
            
        Returns:
            Dictionary with memory creation result
        """
        if not self.client:
            logger.error("Mem0 client not initialized")
            return {"error": "Memory service not available"}
        
        try:
            logger.info(f"Adding memory for user {user_id} with {len(messages)} messages")
            
            # Use the same format as JavaScript examples
            options = {
                "user_id": user_id,
                "version": "v2"
            }
            
            if metadata:
                options.update(metadata)
            
            # Add memories using the client (like JavaScript examples)
            result = self.client.add(messages, **options)
            
            logger.info(f"Successfully added memory for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error adding memory for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def search_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories (like JavaScript examples)
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of memories to return
            categories: Optional categories to filter by
            
        Returns:
            List of relevant memories
        """
        if not self.client:
            logger.error("Mem0 client not initialized")
            return []
        
        try:
            logger.info(f"Searching memories for user {user_id} with query: {query}")
            
            # Use the same format as JavaScript examples
            options = {
                "version": "v2",
                "user_id": user_id
            }
            
            if categories:
                options["categories"] = categories
            
            # Search memories using the client (like JavaScript examples)
            memories = self.client.search(query, **options)
            
            # Limit results
            if limit and len(memories) > limit:
                memories = memories[:limit]
            
            logger.info(f"Found {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {str(e)}")
            return []
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of all user memories
        """
        if not self.client:
            logger.error("Mem0 client not initialized")
            return []
        
        try:
            logger.info(f"Retrieving all memories for user {user_id}")
            
            # Use search with broad query to get all memories
            memories = self.client.search(
                "",  # Empty query to get all
                **{
                    "version": "v2",
                    "user_id": user_id
                }
            )
            
            logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories for user {user_id}: {str(e)}")
            return []
    
    async def delete_memory(self, memory_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a specific memory
        
        Args:
            memory_id: Memory identifier
            user_id: User identifier
            
        Returns:
            Dictionary with deletion result
        """
        if not self.client:
            logger.error("Mem0 client not initialized")
            return {"error": "Memory service not available"}
        
        try:
            logger.info(f"Deleting memory {memory_id} for user {user_id}")
            
            # Delete memory using the client
            result = self.client.delete(memory_id, **{"user_id": user_id})
            
            logger.info(f"Successfully deleted memory {memory_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id} for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def delete_all_memories(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all memories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with deletion result
        """
        if not self.client:
            logger.error("Mem0 client not initialized")
            return {"error": "Memory service not available"}
        
        try:
            logger.info(f"Deleting all memories for user {user_id}")
            
            # Get all memories first
            memories = await self.get_all_memories(user_id)
            
            # Delete each memory
            deleted_count = 0
            for memory in memories:
                if 'id' in memory:
                    result = self.client.delete(memory['id'], **{"user_id": user_id})
                    if 'error' not in result:
                        deleted_count += 1
            
            logger.info(f"Successfully deleted {deleted_count} memories for user {user_id}")
            return {"deleted_count": deleted_count, "total_memories": len(memories)}
            
        except Exception as e:
            logger.error(f"Error deleting all memories for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.client:
            return {"error": "Memory service not available"}
        
        try:
            return {
                "status": "active",
                "provider": "mem0",
                "api_version": "v2",
                "client_initialized": True
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {str(e)}")
            return {"error": str(e)}

# Global Mem0 service instance
mem0_service = Mem0Service()
