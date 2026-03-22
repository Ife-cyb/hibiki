export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface SearchResponse {
  query: string;
  results: {
    anime_id: string;
    title: string;
    synopsis: string;
    image_url: string;
    score: number;
    match_percentage: number;
  }[];
  total_results: number;
  search_time_ms: number;
}

export interface AnimeDetailResponse {
  anime_id: string;
  title: string;
  synopsis: string;
  image_url: string;
  score: number;
  match_percentage?: number;
  genres: string[];
  episodes: number;
  type: string;
}

export async function searchAnime(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to search anime');
  }

  return response.json();
}

export async function getAnimeDetail(animeId: string): Promise<AnimeDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/anime/${animeId}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch anime details');
  }

  return response.json();
}
