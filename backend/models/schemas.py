from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=10, max_length=500, description="The semantic search query for anime discovery.")
    n_results: int = Field(default=6, le=20, description="Number of results to return (max 20).")

class AnimeResult(BaseModel):
    anime_id: str
    title: str
    synopsis: str
    image_url: str
    score: float
    match_percentage: float

class SearchResponse(BaseModel):
    query: str
    results: List[AnimeResult]
    total_results: int
    search_time_ms: float

class AnimeDetailResponse(BaseModel):
    anime_id: str
    title: str
    synopsis: str
    image_url: str
    score: float
    match_percentage: Optional[float] = None
    genres: List[str]
    episodes: int
    type: str

class HealthResponse(BaseModel):
    status: str
    chroma_connected: bool
    total_anime_indexed: int
    version: str

class SearchHistoryEntry(BaseModel):
    id: int
    query: str
    total_results: int
    searched_at: datetime
