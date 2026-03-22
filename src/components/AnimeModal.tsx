import React, { useEffect } from 'react';
import { type AnimeDetailResponse } from '../services/api';

interface AnimeModalProps {
  anime: AnimeDetailResponse;
  onClose: () => void;
}

const AnimeModal: React.FC<AnimeModalProps> = ({ anime, onClose }) => {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in"
      onClick={onClose}
    >
      <div 
        className="bg-[var(--color-mystic-dark)] border border-[var(--color-mystic-purple)]/30 rounded-3xl shadow-[0_0_50px_rgba(155,114,229,0.2)] max-w-4xl w-full overflow-hidden flex flex-col md:flex-row relative transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        <button 
          onClick={onClose} 
          className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center bg-black/50 hover:bg-[var(--color-mystic-purple)]/80 text-white rounded-full transition-colors z-20 backdrop-blur-sm"
          aria-label="Close modal"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="md:w-5/12 h-72 md:h-auto relative">
          <img 
            src={anime.image_url} 
            alt={anime.title} 
            className="w-full h-full object-cover" 
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-mystic-dark)] to-transparent opacity-90 md:hidden" />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[var(--color-mystic-dark)] opacity-90 hidden md:block" />
        </div>

        <div className="p-8 md:w-7/12 flex flex-col justify-center relative z-10 -mt-10 md:mt-0">
          {(anime.match_percentage !== undefined) && (
            <div className="flex items-center gap-2 mb-3">
              <svg className="w-5 h-5 text-[var(--color-mystic-purple)]" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="text-[var(--color-mystic-accent)] font-bold tracking-wider">{anime.match_percentage}% Resonance Match</span>
            </div>
          )}

          <h2 className="text-4xl font-black text-white mb-2 drop-shadow-lg">{anime.title}</h2>
          
          <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-gray-400 font-semibold uppercase tracking-wider">
            <span>{anime.type}</span>
            {anime.episodes > 0 && <span>??? {anime.episodes} EPS</span>}
            <span>??? ??? {anime.score}</span>
          </div>

          <div className="flex flex-wrap gap-2 mb-6">
            {anime.genres.map(g => (
              <span key={g} className="px-3 py-1 bg-[var(--color-mystic-purple)]/10 text-[var(--color-mystic-accent)] rounded-full text-xs font-semibold border border-[var(--color-mystic-purple)]/20 shadow-inner">
                {g}
              </span>
            ))}
          </div>
          
          <div className="flex-grow">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-2">Synopsis</h3>
            <p className="text-gray-300 leading-relaxed text-sm max-h-48 overflow-y-auto pr-2 custom-scrollbar">
              {anime.synopsis}
            </p>
          </div>
          
          <div className="mt-8">
            <a 
              href={`https://myanimelist.net/anime.php?q=${encodeURIComponent(anime.title)}`}
              target="_blank" 
              rel="noreferrer" 
              className="inline-flex items-center gap-2 px-8 py-3 bg-[var(--color-mystic-purple)] hover:bg-[var(--color-mystic-accent)] text-[var(--color-mystic-base)] font-bold rounded-xl transition-all duration-300 shadow-[0_0_15px_rgba(155,114,229,0.3)] hover:shadow-[0_0_25px_rgba(196,169,242,0.6)] hover:-translate-y-0.5"
            >
              <span>Find on MyAnimeList</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnimeModal;
