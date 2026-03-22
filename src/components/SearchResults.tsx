import React, { useState } from 'react';
import AnimeCard from './AnimeCard';
import AnimeModal from './AnimeModal';
import { getAnimeDetail, type AnimeDetailResponse } from '../services/api';
import Toast from './Toast';

export interface AnimeResult {
  anime_id: string;
  title: string;
  synopsis: string;
  image_url: string;
  match_percentage: number;
  score: number;
}

interface SearchResultsProps {
  results: AnimeResult[];
  isLoading: boolean;
}

const SkeletonCard: React.FC = () => (
  <div className="flex flex-col bg-[var(--color-mystic-dark)] border border-gray-800 rounded-2xl overflow-hidden h-full animate-pulse">
    <div className="w-full h-56 bg-gray-800/50"></div>
    <div className="p-5 flex flex-col flex-grow relative z-10 -mt-2 space-y-4">
      <div className="h-6 bg-gray-800/70 rounded w-3/4"></div>
      <div className="space-y-2 mt-2">
        <div className="h-4 bg-gray-800/40 rounded w-full"></div>
        <div className="h-4 bg-gray-800/40 rounded w-5/6"></div>
        <div className="h-4 bg-gray-800/40 rounded w-4/6"></div>
      </div>
    </div>
  </div>
);

const SearchResults: React.FC<SearchResultsProps> = ({ results, isLoading }) => {
  const [selectedAnime, setSelectedAnime] = useState<AnimeDetailResponse | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCardClick = async (anime: AnimeResult) => {
    setIsDetailLoading(true);
    try {
      const details = await getAnimeDetail(anime.anime_id);
      // Optional: Preserve the search match percentage in the detail view
      details.match_percentage = anime.match_percentage;
      setSelectedAnime(details);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch anime details');
    } finally {
      setIsDetailLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <SkeletonCard key={`skeleton-${i}`} />
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="w-full py-12 text-center text-gray-500 animate-fade-in-up">
        No harmonic matches found for this feeling. Try a different resonance.
      </div>
    );
  }

  return (
    <>
      {error && <Toast message={error} onClose={() => setError(null)} />}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 animate-fade-in-up">
        {results.map((anime) => (
          <AnimeCard 
            key={anime.anime_id}
            title={anime.title}
            synopsis={anime.synopsis}
            imageUrl={anime.image_url}
            matchScore={anime.match_percentage}
            onClick={() => handleCardClick(anime)}
          />
        ))}
      </div>

      {/* Optional tiny loading indicator if details take a second to fetch */}
      {isDetailLoading && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fade-in">
           <div className="w-12 h-12 border-4 border-[var(--color-mystic-purple)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {selectedAnime && (
        <AnimeModal 
          anime={selectedAnime} 
          onClose={() => setSelectedAnime(null)} 
        />
      )}
    </>
  );
};

export default SearchResults;
