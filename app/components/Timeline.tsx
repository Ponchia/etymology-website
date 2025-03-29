'use client';

import React from 'react';
import { RootWord, languageColors } from '../types';

export default function Timeline({ words }: { words: RootWord[] }) {
  const wordsWithYears = words.filter(word => word.year != null)
    .sort((a, b) => (a.year as number) - (b.year as number));
  
  if (wordsWithYears.length <= 1) {
    return <div className="text-center text-xs text-gray-500">Not enough dated words</div>;
  }

  // Find min/max years
  const years = wordsWithYears.map(word => word.year as number);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  const yearRange = maxYear - minYear;
  
  return (
    <div className="w-full">
      {/* Timeline header */}
      <div className="flex justify-between text-xs mb-1">
        <span className="font-medium">Timeline</span>
        <span className="text-gray-500">
          {minYear < 0 ? `${Math.abs(minYear)} BCE` : minYear} — {maxYear < 0 ? `${Math.abs(maxYear)} BCE` : maxYear}
        </span>
      </div>
      
      {/* Timeline visualization */}
      <div className="relative h-6">
        {/* Horizontal line */}
        <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-gray-200"></div>
        
        {/* Word markers */}
        {wordsWithYears.map((word, index) => {
          const yearValue = word.year as number;
          const position = ((yearValue - minYear) / yearRange) * 100;
          
          const languageColor = word.language && languageColors[word.language] 
            ? languageColors[word.language].split(' ')[0]
            : 'bg-gray-700';
          
          return (
            <div
              key={`word-${index}`}
              className="absolute" 
              style={{ 
                left: `${position}%`,
                top: '50%',
                transform: 'translate(-50%, -50%)'
              }}
              title={`${word.word} (${yearValue < 0 ? `${Math.abs(yearValue)} BCE` : yearValue})`}
            >
              <div className={`h-2 w-2 ${languageColor} rounded-full`}></div>
            </div>
          );
        })}
      </div>
    </div>
  );
} 