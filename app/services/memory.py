"""
Enhanced memory service integrating Mem0 for intelligent memory management
Combines in-memory conversation history with Mem0 for persistent, semantic memory
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from app.models.chat import MemoryEntry
from app.services.mem0_service import mem0_service

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Enhanced memory service combining conversation history with Mem0 intelligent memory
    """
    
    def __init__(self):
        """Initialize memory service with Mem0 integration"""
        self.memories: Dict[str, List[Dict]] = {}  # user_id -> list of conversations
        self.max_memories_per_user = 50  # Limit to prevent memory bloat
        self.mem0_service = mem0_service
        # Cache for Mem0 memories to reduce API calls
        self.mem0_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.cache_timeout = 300  # 5 minutes
        logger.info("Enhanced memory service initialized with Mem0 integration and caching")
    
    def add_conversation(
        self, 
        user_id: str, 
        user_message: str, 
        assistant_response: str
    ) -> None:
        """
        Add a conversation to memory (both local and Mem0)
        
        Args:
            user_id: User identifier
            user_message: User's message
            assistant_response: Assistant's response
        """
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        conversation = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response
        }
        
        self.memories[user_id].append(conversation)
        
        # Limit memory size
        if len(self.memories[user_id]) > self.max_memories_per_user:
            self.memories[user_id] = self.memories[user_id][-self.max_memories_per_user:]
        
        # Store important information in Mem0 (background task - non-blocking)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            # Create background task that doesn't block the response
            loop.create_task(self._store_important_memories(user_id, user_message, assistant_response))
        except RuntimeError:
            # If no event loop is running, run in background
            import threading
            def store_memory():
                asyncio.run(self._store_important_memories(user_id, user_message, assistant_response))
            threading.Thread(target=store_memory, daemon=True).start()
        
        logger.info(f"Added conversation to memory for user {user_id}")
    
    async def _store_important_memories(
        self, 
        user_id: str, 
        user_message: str, 
        assistant_response: str
    ) -> None:
        """
        Store important information from conversation in Mem0 (like JavaScript examples)
        
        Args:
            user_id: User identifier
            user_message: User's message
            assistant_response: Assistant's response
        """
        try:
            # Create messages array like JavaScript examples
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response}
            ]
            
            # Store in Mem0 with metadata (like JavaScript examples)
            metadata = {
                "timestamp": int(datetime.now().timestamp()),  # Use local time instead of UTC
                "type": "conversation",
                "user_message_length": len(user_message),
                "assistant_response_length": len(assistant_response),
                "timezone": "local"
            }
            
            # Call the async Mem0 operation directly
            await self.mem0_service.add_memory(user_id, messages, metadata)
                
        except Exception as e:
            logger.error(f"Error storing memory in Mem0 for user {user_id}: {str(e)}")
    
    def get_conversation_history(
        self, 
        user_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        if user_id not in self.memories:
            return []
        
        history = self.memories[user_id]
        if limit:
            history = history[-limit:]
        
        logger.info(f"Retrieved {len(history)} conversations for user {user_id}")
        return history
    
    def get_recent_messages_for_context(
        self, 
        user_id: str, 
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get recent messages formatted for OpenAI context
        
        Args:
            user_id: User identifier
            max_messages: Maximum number of message pairs to include
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        history = self.get_conversation_history(user_id, limit=max_messages)
        messages = []
        
        for conv in history:
            messages.append({"role": "user", "content": conv["user_message"]})
            messages.append({"role": "assistant", "content": conv["assistant_response"]})
        
        return messages
    
    async def get_relevant_memories(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get relevant memories from Mem0 for context
        
        Args:
            user_id: User identifier
            query: Query to find relevant memories
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories from Mem0
        """
        try:
            memories = await self.mem0_service.search_memories(user_id, query, limit)
            logger.info(f"Retrieved {len(memories)} relevant memories for user {user_id}")
            return memories
        except Exception as e:
            logger.error(f"Error retrieving relevant memories for user {user_id}: {str(e)}")
            return []
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a user from Mem0 with caching
        
        Args:
            user_id: User identifier
            
        Returns:
            List of all user memories from Mem0
        """
        try:
            # Check cache first
            cache_key = f"{user_id}_all"
            if cache_key in self.mem0_cache:
                logger.info(f"Using cached memories for user {user_id}")
                return self.mem0_cache[cache_key]
            
            # Fetch from Mem0 API
            memories = await self.mem0_service.get_all_memories(user_id)
            
            # Cache the result
            self.mem0_cache[cache_key] = memories
            
            logger.info(f"Retrieved {len(memories)} total memories for user {user_id}")
            return memories
        except Exception as e:
            logger.error(f"Error retrieving all memories for user {user_id}: {str(e)}")
            return []
    
    async def add_important_fact(
        self, 
        user_id: str, 
        fact: str, 
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store an important fact about the user in Mem0 (like JavaScript examples)
        
        Args:
            user_id: User identifier
            fact: Important fact to remember
            importance: Importance score (0-1)
            metadata: Optional metadata
            
        Returns:
            Dictionary with storage result
        """
        try:
            # Create messages array like JavaScript examples
            messages = [
                {"role": "user", "content": f"Important fact: {fact}"},
                {"role": "assistant", "content": f"I'll remember that: {fact}"}
            ]
            
            fact_metadata = {
                "type": "important_fact",
                "importance": importance,
                "timestamp": int(datetime.now().timestamp()),  # Use local time
                "timezone": "local",
                **(metadata or {})
            }
            
            result = await self.mem0_service.add_memory(user_id, messages, fact_metadata)
            
            # Clear cache for this user since we added new memory
            cache_key = f"{user_id}_all"
            if cache_key in self.mem0_cache:
                del self.mem0_cache[cache_key]
            
            logger.info(f"Stored important fact for user {user_id}: {fact[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error storing important fact for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def delete_memory(self, memory_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a specific memory from Mem0
        
        Args:
            memory_id: Memory identifier
            user_id: User identifier
            
        Returns:
            Dictionary with deletion result
        """
        try:
            result = await self.mem0_service.delete_memory(memory_id, user_id)
            logger.info(f"Deleted memory {memory_id} for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id} for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def clear_user_memories(self, user_id: str) -> Dict[str, Any]:
        """
        Clear all memories for a specific user (both local and Mem0)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with clearing result
        """
        try:
            # Clear local conversation history
            if user_id in self.memories:
                del self.memories[user_id]
            
            # Clear Mem0 memories
            mem0_result = await self.mem0_service.delete_all_memories(user_id)
            
            logger.info(f"Cleared all memories for user {user_id}")
            return {
                "local_cleared": True,
                "mem0_result": mem0_result
            }
        except Exception as e:
            logger.error(f"Error clearing memories for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    def get_memory_stats(self) -> Dict[str, int]:
        """
        Get memory statistics
        
        Returns:
            Dictionary with memory statistics
        """
        total_users = len(self.memories)
        total_conversations = sum(len(convs) for convs in self.memories.values())
        
        return {
            "total_users": total_users,
            "total_conversations": total_conversations,
            "max_memories_per_user": self.max_memories_per_user,
            "mem0_integration": "active"
        }
    
    async def get_enhanced_context(
        self, 
        user_id: str, 
        current_message: str,
        max_recent_messages: int = 5,
        max_relevant_memories: int = 3
    ) -> List[Dict[str, str]]:
        """
        Get enhanced context combining recent messages and relevant memories
        
        Args:
            user_id: User identifier
            current_message: Current user message
            max_recent_messages: Maximum recent messages to include
            max_relevant_memories: Maximum relevant memories to include
            
        Returns:
            List of messages for OpenAI context
        """
        try:
            # Get recent conversation history
            recent_messages = self.get_recent_messages_for_context(
                user_id, max_recent_messages
            )
            
            # Get relevant memories from Mem0
            relevant_memories = await self.get_relevant_memories(
                user_id, current_message, max_relevant_memories
            )
            
            # Build enhanced context
            enhanced_context = []
            
            # Add relevant memories as system context
            if relevant_memories:
                memory_context = "Relevant memories: "
                for memory in relevant_memories:
                    if 'memory' in memory:
                        memory_context += f"{memory['memory']}; "
                
                enhanced_context.append({
                    "role": "system",
                    "content": memory_context
                })
            
            # Add recent conversation history
            enhanced_context.extend(recent_messages)
            
            logger.info(f"Built enhanced context for user {user_id}: {len(enhanced_context)} messages")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error building enhanced context for user {user_id}: {str(e)}")
            # Fallback to just recent messages
            return self.get_recent_messages_for_context(user_id, max_recent_messages)

# Global enhanced memory service instance
memory_service = MemoryService()
