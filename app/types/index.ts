// Languages
export type Language = 
  | 'English' 
  | 'Latin' 
  | 'Greek' 
  | 'French' 
  | 'German'
  | 'Proto-Indo-European'
  | 'Proto-Italic'
  | 'Old Norse'
  | 'Old English'
  | 'Sanskrit'
  | string; // For other languages not explicitly defined

// Year related types
export type YearValue = number | null;

export interface Year {
  value: YearValue;
  era?: 'CE' | 'BCE';
  approximate?: boolean;
  display: string; // Formatted string for display (e.g., "1570", "250 BCE", "~800 BCE")
}

// Enhanced word definitions
export interface WordDefinition {
  short: string; // Brief definition for display in flow diagram
  full?: string; // More comprehensive definition, possibly with examples
  senses?: string[]; // Multiple meanings or senses of the word
}

// Base word interface with enhanced typing
export interface RootWord {
  word: string;
  language: Language;
  definition?: string | WordDefinition;
  year?: YearValue;
  roots?: RootWord[];
}

// Etymology word with additional fields
export interface EtymologyWord extends RootWord {
  etymology?: EtymologyWord[];
  derivedTerms?: string[]; // Modern words derived from this one
  cognates?: string[]; // Related words in other languages
}

// Helper function to format years for display
export function formatYear(year: YearValue): string {
  if (year === null) return '';
  return year > 0 ? year.toString() : `${Math.abs(year)} BCE`;
}

// Enhanced language color mapping
export interface LanguageColor {
  [key: string]: string;
}

export const languageColors: LanguageColor = {
  English: 'bg-etymology-blue text-white',
  Latin: 'bg-etymology-purple text-white',
  Greek: 'bg-etymology-red text-white',
  French: 'bg-etymology-yellow text-black',
  German: 'bg-etymology-green text-white',
  'Proto-Indo-European': 'bg-etymology-teal text-white',
  'Proto-Italic': 'bg-etymology-indigo text-white',
  'Old Norse': 'bg-etymology-pink text-white',
  'Old English': 'bg-etymology-orange text-white',
  'Sanskrit': 'bg-etymology-lime text-white',
  // Add more languages as needed
  default: 'bg-gray-700 text-white'
}; 