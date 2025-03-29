export interface RootWord {
  word: string;
  language: string;
  definition?: string;
  year?: number | null;
  roots?: RootWord[];
}

export interface EtymologyWord extends RootWord {
  etymology?: EtymologyWord[];
}

export interface LanguageColor {
  [key: string]: string;
}

export const languageColors: LanguageColor = {
  English: 'bg-etymology-blue text-white',
  Latin: 'bg-etymology-purple text-white',
  Greek: 'bg-etymology-red text-white',
  French: 'bg-etymology-yellow text-black',
  German: 'bg-etymology-green text-white',
  // Add more languages as needed
  default: 'bg-gray-700 text-white'
}; 