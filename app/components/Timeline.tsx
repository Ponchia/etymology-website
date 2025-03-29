'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { RootWord } from '../types';

interface TimelineProps {
  words: RootWord[];
}

export default function Timeline({ words }: TimelineProps) {
  const wordsWithYears = words.filter(word => word.year != null);
  
  if (wordsWithYears.length <= 1) {
    return null; // Don't show timeline if there's only one or no dated items
  }

  // Find the min and max years
  const years = wordsWithYears.map(word => word.year as number);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  const yearRange = maxYear - minYear;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="hidden md:block absolute right-10 h-full max-h-[80vh] w-48"
    >
      <div className="relative h-full">
        {/* Vertical line */}
        <div className="absolute left-6 top-4 bottom-4 w-px bg-gray-300"></div>
        
        {/* Year markers */}
        {wordsWithYears.map((word, index) => {
          const yearPosition = yearRange > 0 
            ? ((word.year as number) - minYear) / yearRange 
            : 0.5;
          const topPosition = `${4 + yearPosition * 92}%`;
          
          return (
            <motion.div
              key={`year-${index}`}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              className="absolute left-0 flex items-center"
              style={{ top: topPosition }}
            >
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
              <div className="ml-4 text-sm">
                <div className="font-bold">{word.year}</div>
                <div className="text-xs opacity-70">{word.word}</div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
} 