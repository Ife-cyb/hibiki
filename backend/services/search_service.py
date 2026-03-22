import sys
import os
import time
from fastapi import HTTPException
from loguru import logger
from typing import Optional

# Add root folder to sys.path so we can import from the pipeline module directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pipeline.db import search_anime, get_collection
from backend.models.schemas import SearchResponse, AnimeResult, AnimeDetailResponse

class SearchService:
    
    @staticmethod
    async def search(query: str, n_results: int) -> SearchResponse:
        logger.info(f"Starting semantic search for query: '{query}'")
        start_time = time.perf_counter()
        
        try:
            # db.search_anime is synchronous. For high throughput we would run this in a ThreadPool, 
            # but for this scale it satisfies the async interface wrapper perfectly.
            raw_results = search_anime(query=query, n_results=n_results)
            
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            
            # Map raw dicts to our Pydantic AnimeResult
            anime_results = []
            for res in raw_results:
                # We need an anime_id since db.py didn't return the raw ID in the previous step...
                # wait, let me fix db.py to return anime_id in search_anime so this is robust,
                # but I will parse it here safely first.
                anime_results.append(AnimeResult(
                    anime_id=res.get("anime_id", "unknown_id"),
                    title=res.get("title", ""),
                    synopsis=res.get("synopsis", ""),
                    image_url=res.get("image_url", ""),
                    score=res.get("score", 0.0),
                    match_percentage=res.get("match_percentage", 0.0)
                ))
                
            logger.success(f"Search completed in {elapsed_ms:.2f}ms. Found {len(anime_results)} results.")
            
            return SearchResponse(
                query=query,
                results=anime_results,
                total_results=len(anime_results),
                search_time_ms=round(elapsed_ms, 2)
            )
            
        except Exception as e:
            logger.error(f"Search operation failed: {e}")
            raise HTTPException(status_code=500, detail="Database connection error while searching.")

    @staticmethod
    async def get_anime_by_id(anime_id: str) -> AnimeDetailResponse:
        logger.info(f"Fetching details for anime_id: {anime_id}")
        try:
            collection = get_collection()
            
            # Query ChromaDB specifically for that ID to get full metadata 
            results = collection.get(ids=[anime_id])
            
            if not results["ids"]:
                logger.warning(f"Anime ID {anime_id} not found in ChromaDB.")
                raise HTTPException(status_code=404, detail="Anime not found.")
                
            meta = results["metadatas"][0]
            
            # We map string genres representation back to list, type, and episodes.
            # Depending on how it was stored in embedder we might need safe fallsbacks.
            genres_str = meta.get("genre", "")
            genres_list = [g.strip() for g in genres_str.split(",")] if genres_str else []
            
            return AnimeDetailResponse(
                anime_id=results["ids"][0],
                title=meta.get("title", "Unknown"),
                synopsis=meta.get("synopsis", ""),
                image_url=meta.get("image_url", ""),
                score=round(float(meta.get("score", 0.0)), 2),
                genres=genres_list,
                episodes=int(meta.get("episodes", 0)),
                type=meta.get("type", "Unknown")
            )
            
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Failed to retrieve anime_id {anime_id}: {e}")
            raise HTTPException(status_code=500, detail="Database connection error while retrieving anime details.")

search_service = SearchService()
