import time
import sqlite3
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from loguru import logger

from backend.models.schemas import SearchRequest, SearchResponse
from backend.services.search_service import search_service

router = APIRouter()

# Simple In-Memory Rate Limiting
# Maps IP Address -> List of timestamps
RATE_LIMIT = 30
RATE_LIMIT_WINDOW = 60 # seconds
rate_tracker: Dict[str, List[float]] = defaultdict(list)

# SQLite initialization for history
DB_PATH = "history.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS search_history
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           query TEXT,
                           total_results INTEGER,
                           searched_at TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

init_db()

def log_search_history(query: str, total_results: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (query, total_results, searched_at) VALUES (?, ?, ?)",
            (query, total_results, datetime.now())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log search history: {e}")

def check_rate_limit(ip: str):
    """Enforces a limit of 30 requests per minute per IP."""
    now = time.time()
    # Prune old request timestamps safely
    rate_tracker[ip] = [t for t in rate_tracker[ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(rate_tracker[ip]) >= RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. You are limited to 30 searches per minute. Please wait."
        )
    
    rate_tracker[ip].append(now)

@router.options("/search", tags=["Search"])
async def search_options():
    return {}

@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def perform_search(request: Request, body: SearchRequest):
    """
    **Semantic Anime Search Endpoint**
    
    Accepts a natural language query describing an anime.
    Embeds the user's query and performs a vector similarity search across the ChromaDB database.
    
    - **query**: The description of what you are looking for. (Minimum 10 non-whitespace characters)
    - **n_results**: How many results to return (Default 6, Max 20)
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    # Custom Validation: Check stripped length to avoid passing on "          " (whitespace queries)
    clean_query = body.query.strip()
    if not clean_query or len(clean_query) < 10:
        raise HTTPException(
            status_code=422,
            detail="Your complete query description is too short! Please provide at least 10 meaningful characters to get accurate recommendations."
        )

    # Perform the semantic search
    response = await search_service.search(query=clean_query, n_results=body.n_results)

    # Log to SQLite
    log_search_history(query=clean_query, total_results=response.total_results)

    return response
