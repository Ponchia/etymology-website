'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { RootWord, languageColors } from '../types';

interface EtymologyCardProps {
  word: RootWord;
  index: number;
  total: number;
}

export default function EtymologyCard({ word, index, total }: EtymologyCardProps) {
  const languageColor = word.language && languageColors[word.language] 
    ? languageColors[word.language] 
    : languageColors.default;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="relative"
    >
      <div className={`rounded-lg p-5 shadow-md ${languageColor} max-w-xs my-2`}>
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xl font-bold">{word.word}</h3>
          <span className="text-xs opacity-80">{word.language}</span>
        </div>
        
        {word.definition && (
          <p className="text-sm mb-2">{word.definition}</p>
        )}
        
        {word.year && (
          <div className="text-xs mt-2">
            First recorded: {word.year}
          </div>
        )}
      </div>

      {/* Connection line if not the last item */}
      {index < total - 1 && (
        <div className="absolute w-px h-10 bg-gray-300 left-1/2 transform -translate-x-1/2 -bottom-10"></div>
      )}
    </motion.div>
  );
} 