import sqlite3
import os
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
from loguru import logger

from backend.models.schemas import SearchHistoryEntry

router = APIRouter()
DB_PATH = "history.db"

# Admin Token Protection
admin_token_header = APIKeyHeader(name="ADMIN_TOKEN", auto_error=False)

def verify_admin_token(api_key: str = Depends(admin_token_header)):
    expected_token = os.getenv("ADMIN_TOKEN")
    if not expected_token:
        logger.error("ADMIN_TOKEN environment variable not set.")
        raise HTTPException(status_code=403, detail="Forbidden")
    if api_key != expected_token:
        raise HTTPException(status_code=403, detail="Forbidden")

def init_db():
    """Initializes the SQLite database and creates the required tables if missing."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                total_results INTEGER NOT NULL,
                searched_at TIMESTAMP NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("SQLite history database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite history db: {e}")

init_db()

@router.get("/api/history", response_model=List[SearchHistoryEntry], tags=["History"], dependencies=[Depends(verify_admin_token)])
async def get_search_history():
    """
    **Get Recent Search History**

    Retrieves the 20 most recent search queries issued to the Hibiki API, 
    ordered from newest to oldest. Requires ADMIN_TOKEN header.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enables column access by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, query, total_results, searched_at 
            FROM search_history 
            ORDER BY searched_at DESC 
            LIMIT 20
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            # Parse the sqlite text timestamp back into a standard Python datetime obj
            try:
                dt = datetime.fromisoformat(row["searched_at"])
            except ValueError:
                # Fallback if manual insertions messed up the format
                dt = datetime.now()
                
            history.append(SearchHistoryEntry(
                id=row["id"],
                query=row["query"],
                total_results=row["total_results"],
                searched_at=dt
            ))
            
        return history
        
    except Exception as e:
        logger.error(f"Error fetching search history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history from database.")

@router.delete("/api/history", tags=["History"], dependencies=[Depends(verify_admin_token)])
async def clear_search_history():
    """
    **Clear Search History**

    Completely truncates the search_history SQLite table. Requires ADMIN_TOKEN header.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history")
        conn.commit()
        
        # Reset the auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='search_history'")
        conn.commit()
        
        conn.close()
        logger.info("Search history cleared explicitly via API.")
        return {"message": "Search history successfully cleared."}
        
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history from database.")
