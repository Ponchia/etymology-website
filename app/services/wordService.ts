'use client';

import { EtymologyWord } from '../types';
import { Octokit } from 'octokit';

// Repository settings
const REPO_OWNER = 'Ponchia';
const REPO_NAME = 'etymology-website';
const DATA_PATH = 'data/words';

// In development, use a sample file for demonstration
// In production, fetch from GitHub repository
const isDev = process.env.NODE_ENV === 'development';

// Initialize Octokit without authentication for public repos
// For private repos, you would need to provide an authentication token
const octokit = new Octokit();

// Helper function to flatten the etymology tree into an array for display
export function flattenEtymologyTree(word: EtymologyWord): EtymologyWord[] {
  const result: EtymologyWord[] = [];
  
  // Start with the main word
  result.push(word);
  
  // Add etymology chain
  if (word.etymology && word.etymology.length > 0) {
    for (const etymWord of word.etymology) {
      result.push(etymWord);
    }
  }
  
  // Add roots
  const processRoots = (rootWord: EtymologyWord, depth = 0) => {
    if (rootWord.roots && rootWord.roots.length > 0) {
      for (const root of rootWord.roots) {
        result.push(root);
        processRoots(root, depth + 1);
      }
    }
  };
  
  if (word.roots && word.roots.length > 0) {
    for (const root of word.roots) {
      result.push(root);
      processRoots(root);
    }
  }
  
  return result;
}

// Sample data for development and fallback
const SAMPLE_DATA: Record<string, EtymologyWord> = {
  "etymology": {
    "word": "etymology",
    "language": "English",
    "year": 1398,
    "definition": "the study of the origin and history of words",
    "etymology": [
      {
        "word": "etymologia",
        "language": "Latin",
        "year": 1350
      }
    ],
    "roots": [
      {
        "word": "etymologia",
        "language": "Latin",
        "definition": "origin of words",
        "year": 1350,
        "roots": [
          {
            "word": "etymon",
            "language": "Greek",
            "definition": "true sense",
            "year": null,
            "roots": [
              {
                "word": "etymos",
                "language": "Greek",
                "definition": "true, real, actual",
                "year": null
              }
            ]
          },
          {
            "word": "logia",
            "language": "Greek",
            "definition": "study of",
            "year": null,
            "roots": [
              {
                "word": "logos",
                "language": "Greek",
                "definition": "word, speech, discourse, reason",
                "year": null
              }
            ]
          }
        ]
      }
    ]
  },
  "philosophy": {
    "word": "philosophy",
    "language": "English",
    "year": 1340,
    "definition": "love or pursuit of wisdom; systematic investigation of the nature of truth",
    "etymology": [
      {
        "word": "philosophie",
        "language": "French",
        "year": 1290,
        "definition": "love of wisdom"
      }
    ],
    "roots": [
      {
        "word": "philosophia",
        "language": "Latin",
        "definition": "the study of philosophy",
        "year": null,
        "roots": [
          {
            "word": "philosophos",
            "language": "Greek",
            "definition": "lover of wisdom",
            "year": null,
            "roots": [
              {
                "word": "philos",
                "language": "Greek",
                "definition": "loving, dear",
                "year": null
              },
              {
                "word": "sophia",
                "language": "Greek",
                "definition": "knowledge, wisdom",
                "year": null,
                "roots": [
                  {
                    "word": "sophos",
                    "language": "Greek",
                    "definition": "wise",
                    "year": null
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "monde": {
    "word": "monde",
    "language": "French",
    "year": 1050,
    "definition": "world, universe, earth",
    "etymology": [],
    "roots": [
      {
        "word": "mundus",
        "language": "Latin",
        "definition": "world, universe, the heavens",
        "year": null,
        "roots": [
          {
            "word": "mundus",
            "language": "Latin",
            "definition": "clean, elegant",
            "year": null,
            "roots": [
              {
                "word": "munde",
                "language": "Latin",
                "definition": "cleanly, neatly",
                "year": null
              }
            ]
          }
        ]
      }
    ]
  },
  "amor": {
    "word": "amor",
    "language": "Latin",
    "year": -100,
    "definition": "love, affection, passion",
    "etymology": [],
    "roots": [
      {
        "word": "ama",
        "language": "Proto-Italic",
        "definition": "love",
        "year": null,
        "roots": [
          {
            "word": "am-",
            "language": "Proto-Indo-European",
            "definition": "mother, nurse",
            "year": null
          }
        ]
      }
    ]
  },
  "polis": {
    "word": "polis",
    "language": "Greek",
    "year": -800,
    "definition": "city, city-state",
    "etymology": [],
    "roots": [
      {
        "word": "pele-",
        "language": "Proto-Indo-European",
        "definition": "citadel, fortified high place",
        "year": null
      }
    ]
  }
};

export async function getWordEtymology(word: string): Promise<EtymologyWord | null> {
  try {
    // Normalize the word (lowercase, remove non-alphanumeric characters)
    const normalizedWord = word.toLowerCase().trim();
    
    // Development mode - use sample data
    if (isDev) {
      console.log('Development mode - using sample data');
      
      // Look for the word in our sample data
      if (SAMPLE_DATA[normalizedWord]) {
        return SAMPLE_DATA[normalizedWord];
      }
      
      // Simulate a delay for loading state demonstration
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Return null for words not in our sample data
      return null;
    } 
    // Production mode - fetch from GitHub
    else {
      console.log('Production mode - fetching from GitHub');
      
      try {
        // First try to fetch directly from raw.githubusercontent.com (more efficient)
        const rawUrl = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${DATA_PATH}/English/${normalizedWord.charAt(0).toLowerCase()}/${normalizedWord}.json`;
        
        try {
          console.log(`Trying raw GitHub URL: ${rawUrl}`);
          const response = await fetch(rawUrl);
          if (response.ok) {
            const data = await response.json();
            console.log('Successfully fetched from raw GitHub URL');
            return data as EtymologyWord;
          }
        } catch (error) {
          console.log('Error fetching from raw GitHub URL, trying API instead:', error);
        }
        
        // Try each language directory
        for (const language of ['English', 'French', 'Latin', 'Greek']) {
          const langRawUrl = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/${DATA_PATH}/${language}/${normalizedWord.charAt(0).toLowerCase()}/${normalizedWord}.json`;
          
          try {
            console.log(`Trying language-specific raw URL: ${langRawUrl}`);
            const langResponse = await fetch(langRawUrl);
            if (langResponse.ok) {
              const data = await langResponse.json();
              console.log(`Successfully fetched from ${language} directory`);
              return data as EtymologyWord;
            }
          } catch {
            console.log(`Error fetching from ${language} directory`);
          }
        }
        
        // Fall back to GitHub API if direct fetch fails
        console.log('Falling back to GitHub API');
        
        // Check each language directory
        for (const language of ['English', 'French', 'Latin', 'Greek']) {
          const filePath = `${DATA_PATH}/${language}/${normalizedWord.charAt(0).toLowerCase()}/${normalizedWord}.json`;
          
          try {
            console.log(`Trying GitHub API with path: ${filePath}`);
            const apiResponse = await octokit.rest.repos.getContent({
              owner: REPO_OWNER,
              repo: REPO_NAME,
              path: filePath,
            });
            
            // If the file exists, decode and parse it
            if (apiResponse.status === 200 && 'content' in apiResponse.data) {
              // GitHub API returns content as base64 encoded
              const content = atob(apiResponse.data.content);
              console.log(`Successfully fetched from GitHub API (${language} directory)`);
              return JSON.parse(content) as EtymologyWord;
            }
          } catch {
            console.log(`Error fetching from GitHub API (${language} directory)`);
          }
        }
        
        // If all API attempts fail, check for fallback data
        console.log('All GitHub fetch attempts failed, checking for fallback data');
        if (SAMPLE_DATA[normalizedWord]) {
          console.log(`Falling back to sample data for "${normalizedWord}"`);
          return SAMPLE_DATA[normalizedWord];
        }
        
        return null;
      } catch (error) {
        console.error('Error in GitHub fetch logic:', error);
        
        // For fallback, return sample data for known words
        if (SAMPLE_DATA[normalizedWord]) {
          console.log(`Falling back to sample data for "${normalizedWord}"`);
          return SAMPLE_DATA[normalizedWord];
        }
        
        return null;
      }
    }
  } catch (error) {
    console.error('Error in getWordEtymology:', error);
    return null;
  }
} 