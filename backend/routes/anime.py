from fastapi import APIRouter

from backend.models.schemas import AnimeDetailResponse
from backend.services.search_service import search_service

router = APIRouter()

@router.get("/api/anime/{anime_id}", response_model=AnimeDetailResponse, tags=["Anime"])
async def get_anime_details(anime_id: str):
    """
    **Get Anime Details by ID**

    Retrieves the complete metadata profile for a specific anime by its universally unique ID.
    Includes additional data like genres list, episode count, and format type.

    - **anime_id**: The UUID of the anime stored in the Chroma database.
    """
    # The search_service.get_anime_by_id automatically raises a 404 HTTPException 
    # if it doesn't resolve in ChromaDB.
    response = await search_service.get_anime_by_id(anime_id)
    return response
