'use client';

import React, { useState } from 'react';
import SearchInput from './components/SearchInput';
import EtymologyFlow from './components/EtymologyFlow';
import { EtymologyWord } from './types';
import { getWordEtymology, flattenEtymologyTree } from './services/wordService';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchedWord, setSearchedWord] = useState<string | null>(null);
  const [etymologyData, setEtymologyData] = useState<EtymologyWord | null>(null);
  const [flattenedWords, setFlattenedWords] = useState<EtymologyWord[]>([]);

  const handleSearch = async (word: string) => {
    setLoading(true);
    setError(null);
    setSearchedWord(word);
    
    try {
      const data = await getWordEtymology(word);
      
      if (!data) {
        setError(`No etymology data found for "${word}"`);
        setEtymologyData(null);
        setFlattenedWords([]);
      } else {
        setEtymologyData(data);
        const flattened = flattenEtymologyTree(data);
        setFlattenedWords(flattened);
      }
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
      setEtymologyData(null);
      setFlattenedWords([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial search screen
  if (!etymologyData && !loading && !error) {
    return (
      <div className="full-page">
        <h1 className="text-4xl font-bold mb-2">Etymology Explorer</h1>
        <p className="text-zinc-400 mb-8">Discover the origins and history of words</p>
        <div className="w-full max-w-md">
          <SearchInput onSearch={handleSearch} />
        </div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="full-page">
        <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        <p className="mt-4">Loading...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="full-page">
        <div className="bg-red-50 text-red-800 p-4 rounded-lg max-w-md">
          {error}
        </div>
        <button 
          onClick={() => {setError(null); setSearchedWord(null);}}
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Results view
  return (
    <div className="h-screen flex flex-col">
      {/* Fixed header */}
      <div className="bg-white/90 p-3 shadow-sm flex justify-between items-center">
        <h1 className="font-bold">
          Etymology of <span className="italic">{searchedWord}</span>
        </h1>
        <div className="w-64">
          <SearchInput onSearch={handleSearch} compact />
        </div>
      </div>
      
      {/* Main content - now takes full remaining height */}
      <div className="flex-1 flow-container">
        <EtymologyFlow words={flattenedWords} />
      </div>
    </div>
  );
} 