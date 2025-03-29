'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchInputProps {
  onSearch: (word: string) => void;
}

export default function SearchInput({ onSearch }: SearchInputProps) {
  const [word, setWord] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (word.trim()) {
      onSearch(word.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      <div className="relative flex items-center">
        <input
          type="text"
          value={word}
          onChange={(e) => setWord(e.target.value)}
          placeholder="Enter a word..."
          className="w-full py-3 px-4 pl-12 rounded-full border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-etymology-blue focus:border-transparent"
        />
        <Search className="absolute left-4 text-gray-400" size={20} />
        <button 
          type="submit"
          className="absolute right-2 p-2 bg-etymology-blue text-white rounded-full hover:bg-blue-600 transition-colors"
          disabled={!word.trim()}
        >
          Search
        </button>
      </div>
    </form>
  );
} 