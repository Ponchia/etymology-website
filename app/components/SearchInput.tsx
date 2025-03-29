'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchInputProps {
  onSearch: (word: string) => void;
  compact?: boolean;
}

export default function SearchInput({ onSearch, compact = false }: SearchInputProps) {
  const [word, setWord] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (word.trim()) {
      onSearch(word.trim());
    }
  };

  // Compact version for the header
  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="w-full">
        <div className="relative">
          <input
            type="text"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            placeholder="Search..."
            className="w-full rounded text-sm p-1 pl-7 pr-16 border border-gray-200"
          />
          <Search className="absolute left-2 top-1.5 text-gray-400" size={14} />
          <button 
            type="submit"
            className="absolute right-1 top-1 rounded bg-blue-500 text-white px-2 py-0.5 text-xs"
            disabled={!word.trim()}
          >
            Search
          </button>
        </div>
      </form>
    );
  }

  // Full version for the homepage
  return (
    <form onSubmit={handleSubmit}>
      <div className="relative">
        <input
          type="text"
          value={word}
          onChange={(e) => setWord(e.target.value)}
          placeholder="Search for a word..."
          className="w-full rounded-lg bg-zinc-800 p-4 pl-12 border border-zinc-600 text-white"
        />
        <Search className="absolute left-4 top-4 text-zinc-400" size={20} />
        <button 
          type="submit"
          className="absolute right-2 top-2 rounded bg-zinc-700 px-4 py-2 text-white"
          disabled={!word.trim()}
        >
          Search
        </button>
      </div>
    </form>
  );
} 