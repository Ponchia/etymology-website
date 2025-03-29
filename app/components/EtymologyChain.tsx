'use client';

import React from 'react';
import { motion } from 'framer-motion';
import EtymologyCard from './EtymologyCard';
import { RootWord } from '../types';

interface EtymologyChainProps {
  words: RootWord[];
}

export default function EtymologyChain({ words }: EtymologyChainProps) {
  if (!words || words.length === 0) {
    return <div>No etymology data found.</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center w-full"
    >
      {words.map((word, index) => (
        <EtymologyCard
          key={`${word.word}-${index}`}
          word={word}
          index={index}
          total={words.length}
        />
      ))}
    </motion.div>
  );
} 