'use client';

import React, { useState } from 'react';
import { Inter } from 'next/font/google';
import SearchInput from './components/SearchInput';
import EtymologyChain from './components/EtymologyChain';
import Timeline from './components/Timeline';
import { EtymologyWord } from './types';
import { getWordEtymology, flattenEtymologyTree } from './services/wordService';

const inter = Inter({ subsets: ['latin'] });

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
      setError(`Error fetching etymology data: ${err instanceof Error ? err.message : String(err)}`);
      setEtymologyData(null);
      setFlattenedWords([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={`min-h-screen p-6 md:p-24 ${inter.className}`}>
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-center">Etymology Explorer</h1>
        
        <div className="flex justify-center mb-12">
          <SearchInput onSearch={handleSearch} />
        </div>

        {loading && (
          <div className="text-center my-10">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            <p className="mt-2">Loading etymology data...</p>
          </div>
        )}

        {error && (
          <div className="text-center my-10 p-4 bg-red-100 text-red-800 rounded-lg">
            {error}
          </div>
        )}

        {!loading && !error && etymologyData && (
          <div className="relative flex flex-col md:flex-row justify-between mt-10">
            <div className="flex-grow">
              <h2 className="text-2xl font-semibold mb-6">
                Etymology of <span className="italic">{searchedWord}</span>
              </h2>
              <EtymologyChain words={flattenedWords} />
            </div>
            
            <Timeline words={flattenedWords} />
          </div>
        )}
      </div>
    </main>
  );
} 