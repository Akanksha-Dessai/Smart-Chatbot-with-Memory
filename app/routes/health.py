"""
Health check routes for monitoring application status
"""

from fastapi import APIRouter
from datetime import datetime
import logging
from app.services.memory import memory_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        dict: Health status and basic information
    """
    try:
        # Get memory statistics
        memory_stats = memory_service.get_memory_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app_name": settings.app_name,
            "version": "1.0.0",
            "memory_stats": memory_stats,
            "openai_model": settings.openai_model
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with more comprehensive information
    
    Returns:
        dict: Detailed health status and system information
    """
    try:
        memory_stats = memory_service.get_memory_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app_name": settings.app_name,
            "version": "1.0.0",
            "debug_mode": settings.debug,
            "openai_config": {
                "model": settings.openai_model,
                "temperature": settings.openai_temperature,
                "max_tokens": settings.openai_max_tokens
            },
            "memory_stats": memory_stats,
            "endpoints": {
                "chat_stream": "/api/chat",
                "chat_simple": "/api/chat/simple",
                "chat_history": "/api/chat/history/{user_id}",
                "health": "/api/health"
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
