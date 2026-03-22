import React from 'react';

export interface AnimeCardProps {
  imageUrl: string;
  title: string;
  synopsis: string;
  matchScore: number;
  onClick?: () => void;
}

const AnimeCard: React.FC<AnimeCardProps> = ({ imageUrl, title, synopsis, matchScore, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="flex flex-col group bg-[var(--color-mystic-dark)] border border-gray-800 hover:border-[var(--color-mystic-purple)] rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_10px_30px_rgba(155,114,229,0.25)] relative h-full cursor-pointer"
    >
      {/* Cover Image Section */}
      <div className="relative w-full h-56 overflow-hidden">
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {/* Absolute positioned gradient overlay for smoother blending */}
        <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-mystic-dark)] to-transparent opacity-80" />
        
        {/* Match Score Badge */}
        <div className="absolute top-3 left-3 bg-[var(--color-mystic-base)]/90 backdrop-blur-md border border-[var(--color-mystic-purple)]/50 text-[var(--color-mystic-accent)] px-3 py-1 rounded-full text-xs font-bold tracking-wider shadow-lg flex items-center gap-1 z-10">
          <svg className="w-3 h-3 text-[var(--color-mystic-purple)]" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          {matchScore}% Match
        </div>
      </div>
      
      {/* Text Content Section */}
      <div className="p-5 flex flex-col flex-grow relative z-10 -mt-8">
        <h3 className="text-xl font-bold text-[var(--color-mystic-light)] truncate drop-shadow-md">
          {title}
        </h3>
        
        <p className="mt-2 text-sm text-gray-400 line-clamp-3 leading-relaxed">
          {synopsis}
        </p>
      </div>
    </div>
  );
};

export default AnimeCard;
