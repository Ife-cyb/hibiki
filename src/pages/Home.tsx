import React, { useState } from 'react';
import SearchResults, { type AnimeResult } from '../components/SearchResults';
import { searchAnime } from '../services/api';
import Toast from '../components/Toast';

const Home: React.FC = () => {
  const [query, setQuery] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<AnimeResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length < 10) {
      setError("Please describe your feeling with at least 10 characters.");
      return;
    }
    
    if (query.trim()) {
      setHasSearched(true);
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await searchAnime(query);
        setResults(response.results);
      } catch (err: any) {
        setError(err.message || 'An error occurred during search.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen px-4 py-20 bg-[var(--color-mystic-base)] text-[var(--color-mystic-light)]">
      {error && <Toast message={error} onClose={() => setError(null)} />}
      
      <div className={`max-w-4xl w-full flex flex-col gap-8 relative z-10 transition-all duration-700 ${hasSearched ? 'items-start' : 'items-center mt-20'}`}>
        
        {/* Header Section */}
        <div className={`text-center space-y-4 transition-all duration-700 ${hasSearched ? 'text-left flex items-center gap-6' : ''}`}>
          <h1 className={`font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-[var(--color-mystic-purple)] to-white filter drop-shadow-[0_0_25px_rgba(155,114,229,0.3)] transition-all duration-700 ${hasSearched ? 'text-5xl' : 'text-7xl'}`}>
            Hibiki
          </h1>
          {!hasSearched && (
            <p className="text-xl text-[var(--color-mystic-accent)] opacity-80 font-light tracking-wide">
              Describe a feeling. Find your anime.
            </p>
          )}
        </div>

        {/* Search Section */}
        <form onSubmit={handleSearch} className={`w-full flex flex-col gap-6 mt-4 transition-all duration-700 ${hasSearched ? 'max-w-4xl flex-row items-stretch' : 'items-center'}`}>
          <div className="relative w-full group flex-grow">
            <div className="absolute -inset-1 bg-gradient-to-r from-[var(--color-mystic-purple)] to-[var(--color-mystic-accent)] rounded-2xl blur-md opacity-20 group-focus-within:opacity-50 transition duration-700"></div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSearch(e);
                }
              }}
              placeholder="E.g., A melancholic journey through a quiet, rainy city where characters confront their forgotten pasts..."
              className={`resize-none w-full bg-[var(--color-mystic-dark)] text-lg text-[var(--color-mystic-light)] placeholder:text-gray-600 p-6 rounded-2xl border border-gray-800 focus:outline-none focus:border-[var(--color-mystic-purple)] shadow-inner transition-all duration-500 relative z-10 leading-relaxed ${hasSearched ? 'h-24 py-4' : 'h-40'}`}
            />
          </div>
          
          <button 
            type="submit"
            disabled={isLoading}
            className={`px-10 bg-[var(--color-mystic-purple)] hover:bg-[var(--color-mystic-accent)] text-[var(--color-mystic-base)] font-bold text-lg rounded-2xl shadow-[0_0_15px_rgba(155,114,229,0.4)] hover:shadow-[0_0_25px_rgba(196,169,242,0.6)] hover:-translate-y-0.5 transition-all duration-300 relative z-10 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${hasSearched ? 'h-24' : 'py-3 rounded-full'}`}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {hasSearched && (
        <div className="w-full max-w-5xl mt-16 animate-fade-in-up">
          <h2 className="text-2xl font-semibold mb-8 text-[var(--color-mystic-accent)] opacity-80 border-b border-gray-800 pb-4">
            Harmonic Matches
          </h2>
          <SearchResults isLoading={isLoading} results={results} />
        </div>
      )}
    </div>
  );
};

export default Home;
