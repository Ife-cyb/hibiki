import sys
import os
from fastapi import APIRouter
from loguru import logger

# Add root folder to sys.path so we can import from the pipeline module directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.models.schemas import HealthResponse
from pipeline.db import get_collection

router = APIRouter()

# Avoid circular imports for this simple constant, or declare it fresh.
# We'll expect the main app to have this defined, but realistically hardcoding 
# it centrally or mapping a config class is preferred. For now we mock the constant:
try:
    from backend.main import VERSION
except ImportError:
    VERSION = "1.0.0"

@router.get("/api/health", response_model=HealthResponse, tags=["System"])
async def check_health():
    """
    **System Health Check**

    Verifies the operational status of the API and its connection to the underlying ChromaDB vector store.
    Always returns a 200 OK HTTP status. Degraded connections will be reflected in the payload.
    """
    status = "ok"
    chroma_connected = False
    total_anime_indexed = 0
    
    try:
        # A lightweight ping: get the collection and read its count
        collection = get_collection()
        total_anime_indexed = collection.count()
        chroma_connected = True
        
    except Exception as e:
        logger.warning(f"Health check detected DB degradation: {e}")
        status = "degraded"
        
    return HealthResponse(
        status=status,
        chroma_connected=chroma_connected,
        total_anime_indexed=total_anime_indexed,
        version=VERSION
    )
