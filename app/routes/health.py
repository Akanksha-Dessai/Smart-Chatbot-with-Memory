"""
Health check routes for monitoring application status
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import logging
# Memory service no longer needed - handled by OpenAI tool calls
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
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app_name": settings.app_name,
            "version": "1.0.0",
            "memory_integration": "Mem0 with OpenAI tool calls",
            "openai_model": settings.openai_model
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app_name": settings.app_name,
            "version": "1.0.0",
            "debug_mode": settings.debug,
            "openai_config": {
                "model": settings.openai_model,
                "temperature": settings.openai_temperature,
                "max_tokens": settings.openai_max_tokens
            },
            "memory_integration": "Mem0 with OpenAI tool calls",
            "endpoints": {
                "chat_stream": "/api/chat",
                "health": "/api/health"
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }