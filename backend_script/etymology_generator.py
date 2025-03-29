#!/usr/bin/env python3
import os
import json
import time
import random
import logging
import argparse
import requests
import re
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("etymology_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("etymology_generator")

class EtymologyGenerator:
    def __init__(self, test_mode: bool = False, threads: int = 1, batch_size: int = 10):
        self.test_mode = test_mode
        self.threads = threads
        self.batch_size = batch_size
        self.data_dir = Path("../data/words")
        self.state_file = Path("generator_state.json")
        self.word_sources = {
            "English": ["https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"],
            "French": ["https://raw.githubusercontent.com/lorenbrichter/Words/master/French.txt"],
            "Latin": ["https://raw.githubusercontent.com/bkidwell/latin-word-list/master/latin-words.txt"],
            "Greek": []  # Would need to find a good source
        }
        
        # Language codes for API requests
        self.lang_codes = {
            "English": "en",
            "French": "fr",
            "Latin": "la",
            "Greek": "el"
        }
        
        # Statistics tracking
        self.stats = {
            "total_words_processed": 0,
            "successful_words": 0,
            "failed_words": 0,
            "total_connections": 0,
            "languages": {},
            "last_processed": "",
            "start_time": time.time(),
            "processed_words": set()
        }
        
        # Load existing state if available
        self.load_state()

    def load_state(self):
        """Load previous generator state if it exists"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                saved_state = json.load(f)
                self.stats = saved_state
                self.stats["processed_words"] = set(saved_state.get("processed_words", []))
                logger.info(f"Loaded existing state with {len(self.stats['processed_words'])} processed words")
    
    def save_state(self):
        """Save current generator state"""
        if self.test_mode:
            logger.info("Test mode: state not saved")
            return

        # Convert set to list for JSON serialization
        serializable_stats = {**self.stats}
        serializable_stats["processed_words"] = list(self.stats["processed_words"])
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(serializable_stats, f, indent=2)
        logger.info(f"Saved state with {len(self.stats['processed_words'])} processed words")

    def fetch_word_lists(self) -> Dict[str, List[str]]:
        """Fetch word lists for each language"""
        word_lists = {}
        
        for language, urls in self.word_sources.items():
            word_lists[language] = []
            for url in urls:
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        # Handle different formats (assuming plain text with one word per line)
                        words = [w.strip().lower() for w in response.text.split("\n") if w.strip()]
                        word_lists[language].extend(words)
                        logger.info(f"Fetched {len(words)} {language} words from {url}")
                except Exception as e:
                    logger.error(f"Error fetching {language} words from {url}: {str(e)}")
            
            # Remove duplicates
            word_lists[language] = list(set(word_lists[language]))
            
            # Limit words for testing if needed
            if self.test_mode and len(word_lists[language]) > 100:
                word_lists[language] = word_lists[language][:100]
                logger.info(f"Limited {language} word list to 100 words for testing")
        
        return word_lists

    def fetch_etymology(self, word: str, language: str = "English") -> Optional[Dict]:
        """
        Fetch etymology data for a given word from various sources
        """
        try:
            # First try Wiktionary
            etymology_data = self.fetch_from_wiktionary(word, language)
            
            # If not found, try EtymOnline
            if not etymology_data or not etymology_data.get("roots"):
                etymonline_data = self.fetch_from_etymonline(word, language)
                if etymonline_data:
                    if not etymology_data:
                        etymology_data = etymonline_data
                    else:
                        # Merge data, preferring etymonline for etymology chain
                        if not etymology_data.get("roots") and etymonline_data.get("roots"):
                            etymology_data["roots"] = etymonline_data["roots"]
                        if not etymology_data.get("year") and etymonline_data.get("year"):
                            etymology_data["year"] = etymonline_data["year"]
                
            # As a fallback, try Free Dictionary API
            if not etymology_data:
                etymology_data = self.fetch_from_freedictionary(word, language)

            # If we have data, ensure it's in the right format
            if etymology_data:
                # Fill in missing data with reasonable defaults
                if "year" not in etymology_data:
                    etymology_data["year"] = None
                if "definition" not in etymology_data:
                    etymology_data["definition"] = f"Definition of {word}"
                
                # Add short meaning
                etymology_data = self.add_short_meaning(etymology_data)
                
                # Ensure the etymology array exists (for compatibility)
                if "etymology" not in etymology_data:
                    etymology_data["etymology"] = []
                    # Convert first level of roots to etymology array for compatibility
                    if "roots" in etymology_data and etymology_data["roots"]:
                        for root in etymology_data["roots"]:
                            etymology_data["etymology"].append({
                                "word": root.get("word", ""),
                                "language": root.get("language", ""),
                                "year": root.get("year", None)
                            })
                    
                return etymology_data
                
            return None
        except Exception as e:
            logger.error(f"Error fetching etymology for {word}: {str(e)}")
            return None

    def add_short_meaning(self, etymology_data: Dict) -> Dict:
        """Add a short meaning field (condensed definition)"""
        if "definition" in etymology_data and etymology_data["definition"]:
            # Take first sentence or limit to 50 chars
            definition = etymology_data["definition"]
            short_def = definition.split('.')[0]
            if len(short_def) > 50:
                short_def = short_def[:47] + "..."
            etymology_data["meaning"] = short_def
        return etymology_data

    def fetch_from_wiktionary(self, word: str, language: str) -> Optional[Dict]:
        """Fetch etymology from Wiktionary"""
        try:
            # First get the definition
            url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            definition_data = response.json()
            
            # Then get the complete page content for etymology parsing
            url = f"https://en.wiktionary.org/w/api.php?action=parse&format=json&page={word}&prop=text"
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                # Return just the definition if we have it
                if definition_data:
                    return {
                        "word": word,
                        "language": language,
                        "definition": self.extract_definition(definition_data, language),
                        "year": None,
                        "roots": []
                    }
                return None
            
            page_data = response.json()
            
            # Extract etymology information
            etymology_data = {
                "word": word,
                "language": language,
                "definition": self.extract_definition(definition_data, language),
                "year": self.extract_year_from_wiktionary(page_data),
                "roots": self.extract_roots_from_wiktionary(page_data, word, language)
            }
            
            return etymology_data
        except Exception as e:
            logger.debug(f"Wiktionary lookup failed for {word}: {str(e)}")
            return None

    def extract_year_from_wiktionary(self, data: Dict) -> Optional[int]:
        """Extract year information from Wiktionary data"""
        try:
            if "parse" not in data or "text" not in data["parse"]:
                return None
                
            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for etymology section
            etym_headers = soup.find_all(['h3', 'h4'], string=lambda s: s and 'Etymology' in s)
            
            for header in etym_headers:
                # Get content following this header
                content = []
                for sibling in header.next_siblings:
                    if sibling.name and sibling.name.startswith('h'):
                        break
                    content.append(str(sibling))
                
                etym_text = ' '.join(content)
                
                # Look for year patterns
                year_patterns = [
                    r'from (\d{3,4})',
                    r'in (\d{3,4})',
                    r'circa (\d{3,4})',
                    r'c\. (\d{3,4})',
                    r'around (\d{3,4})',
                    r'attested .*?(\d{3,4})',
                    r'first .*?(\d{3,4})'
                ]
                
                for pattern in year_patterns:
                    match = re.search(pattern, etym_text)
                    if match:
                        year = int(match.group(1))
                        # Validate year is reasonable (years 500-2023)
                        if 500 <= year <= 2023:
                            return year
            
            return None
        except Exception as e:
            logger.debug(f"Error extracting year: {str(e)}")
            return None

    def extract_roots_from_wiktionary(self, data: Dict, word: str, language: str) -> List[Dict]:
        """Extract etymology roots from Wiktionary data"""
        try:
            roots = []
            
            if "parse" not in data or "text" not in data["parse"]:
                return roots
                
            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for etymology section
            etym_headers = soup.find_all(['h3', 'h4'], string=lambda s: s and 'Etymology' in s)
            
            for header in etym_headers:
                # Get all content following this header until the next header
                etym_text = ""
                for sibling in header.next_siblings:
                    if sibling.name and sibling.name.startswith('h'):
                        break
                    etym_text += str(sibling)
                
                if etym_text:
                    # Convert HTML to plain text
                    etym_text = re.sub(r'<[^>]+>', ' ', etym_text)
                    etym_text = re.sub(r'\s+', ' ', etym_text).strip()
                    
                    # Much more specific patterns for extracting root words
                    language_patterns = {
                        "Latin": [
                            r'Latin\s+(\w{3,}[\w-]*)',
                            r'from\s+Latin\s+(\w{3,}[\w-]*)',
                            r'from\s+the\s+Latin\s+(\w{3,}[\w-]*)',
                            r'Latin\s+"([^"]{3,})"',
                            r'Latin\s+word\s+(\w{3,}[\w-]*)'
                        ],
                        "Greek": [
                            r'Greek\s+(\w{3,}[\w-]*)',
                            r'from\s+Greek\s+(\w{3,}[\w-]*)',
                            r'from\s+the\s+Greek\s+(\w{3,}[\w-]*)',
                            r'Greek\s+"([^"]{3,})"',
                            r'Greek\s+word\s+(\w{3,}[\w-]*)'
                        ],
                        "French": [
                            r'French\s+(\w{3,}[\w-]*)',
                            r'from\s+French\s+(\w{3,}[\w-]*)',
                            r'from\s+the\s+French\s+(\w{3,}[\w-]*)',
                            r'French\s+"([^"]{3,})"',
                            r'French\s+word\s+(\w{3,}[\w-]*)'
                        ],
                        "Old English": [
                            r'Old English\s+(\w{3,}[\w-]*)',
                            r'from\s+Old English\s+(\w{3,}[\w-]*)',
                            r'from\s+the\s+Old English\s+(\w{3,}[\w-]*)',
                            r'Old English\s+"([^"]{3,})"',
                            r'Old English\s+word\s+(\w{3,}[\w-]*)'
                        ],
                        "Proto-Germanic": [
                            r'Proto-Germanic\s+(\w{3,}[\w-]*)',
                            r'from\s+Proto-Germanic\s+(\w{3,}[\w-]*)',
                            r'from\s+the\s+Proto-Germanic\s+(\w{3,}[\w-]*)',
                            r'Proto-Germanic\s+"([^"]{3,})"',
                            r'Proto-Germanic\s+word\s+(\w{3,}[\w-]*)'
                        ]
                    }
                    
                    # Try to find exact patterns
                    found_roots = False
                    for root_lang, patterns in language_patterns.items():
                        for pattern in patterns:
                            matches = re.finditer(pattern, etym_text, re.IGNORECASE)
                            for match in matches:
                                root_word = match.group(1).strip('.,:;()[]{}')
                                # Validate the root word - at least 3 chars and not the same as the original
                                if (root_word and 
                                    len(root_word) >= 3 and 
                                    root_word.lower() != word.lower()):
                                    
                                    # Try to find a relevant year
                                    year_match = re.search(r'(\d{3,4})', etym_text[:match.start()])
                                    year = int(year_match.group(1)) if year_match else None
                                    
                                    # Create root entry
                                    root = {
                                        "word": root_word,
                                        "language": root_lang,
                                        "definition": self.get_brief_definition(root_word, root_lang),
                                        "year": year,
                                        "roots": []  # Next level roots would be fetched recursively in a production impl
                                    }
                                    
                                    # Check if this root is already in our list to avoid duplicates
                                    if not any(r.get("word").lower() == root_word.lower() and 
                                              r.get("language") == root_lang for r in roots):
                                        roots.append(root)
                                        found_roots = True
                    
                    # If no roots found with specific patterns, try fallback patterns
                    if not found_roots:
                        # Look for italicized words which often indicate foreign terms
                        italic_patterns = [
                            r'<i>([^<]{3,})</i>',
                            r'<em>([^<]{3,})</em>'
                        ]
                        
                        for pattern in italic_patterns:
                            matches = re.finditer(pattern, html_content)
                            for match in matches:
                                italic_word = match.group(1).strip('.,:;()[]{}')
                                if italic_word and len(italic_word) >= 3 and italic_word.lower() != word.lower():
                                    # Try to determine language
                                    context = html_content[max(0, match.start()-50):min(len(html_content), match.end()+50)]
                                    lang = 'Unknown'
                                    for possible_lang in ['Latin', 'Greek', 'French', 'German', 'Spanish', 'Italian']:
                                        if possible_lang.lower() in context.lower():
                                            lang = possible_lang
                                            break
                                    
                                    # Try to find a relevant year
                                    year_match = re.search(r'(\d{3,4})', context)
                                    year = int(year_match.group(1)) if year_match else None
                                    
                                    # Create root entry
                                    root = {
                                        "word": italic_word,
                                        "language": lang,
                                        "definition": self.get_brief_definition(italic_word, lang),
                                        "year": year,
                                        "roots": []
                                    }
                                    
                                    # Check if this root is already in our list to avoid duplicates
                                    if not any(r.get("word").lower() == italic_word.lower() for r in roots):
                                        roots.append(root)
            
            return roots
        except Exception as e:
            logger.debug(f"Error extracting roots: {str(e)}")
            return []

    def get_brief_definition(self, word: str, language: str) -> str:
        """Get a brief definition for a root word"""
        try:
            lang_code = self.lang_codes.get(language, "en")
            url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang_code}/{word}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings and len(meanings) > 0:
                        definitions = meanings[0].get('definitions', [])
                        if definitions and len(definitions) > 0:
                            definition = definitions[0].get('definition', f"Definition of {word}")
                            # Remove HTML tags
                            definition = re.sub(r'<[^>]+>', '', definition)
                            return definition
            
            return f"Definition of {word}"
        except:
            return f"Definition of {word}"

    def fetch_from_etymonline(self, word: str, language: str) -> Optional[Dict]:
        """Fetch etymology from EtymOnline"""
        if language != "English":
            return None  # EtymOnline primarily covers English words
            
        try:
            url = f"https://www.etymonline.com/word/{word}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main entry
            entry = soup.find('div', class_='word--C9UPa')
            if not entry:
                return None
                
            # Get the definition/etymology text
            etym_section = entry.find('section', class_='word__defination--2q7ZH')
            if not etym_section:
                return None
                
            etym_text = etym_section.get_text()
            
            # Extract year
            year_match = re.search(r'(\d{3,4})', etym_text)
            year = int(year_match.group(1)) if year_match else None
            
            # Extract definition
            definition = etym_text.split('.')[0] if etym_text else f"Definition of {word}"
            
            # Extract root words and their languages
            roots = []
            
            # Common language patterns in etymonline entries
            language_patterns = {
                "Latin": [r'Latin[a-z\s]*(\w+)', r'from Latin[a-z\s]*(\w+)'],
                "Greek": [r'Greek[a-z\s]*(\w+)', r'from Greek[a-z\s]*(\w+)'],
                "French": [r'French[a-z\s]*(\w+)', r'from French[a-z\s]*(\w+)'],
                "Old English": [r'Old English[a-z\s]*(\w+)', r'from Old English[a-z\s]*(\w+)'],
                "Proto-Germanic": [r'Proto-Germanic[a-z\s]*(\w+)', r'from Proto-Germanic[a-z\s]*(\w+)'],
            }
            
            for root_lang, patterns in language_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, etym_text)
                    for match in matches:
                        root_word = match.group(1).strip('.,:;')
                        if root_word and root_word != word:  # Avoid self-reference
                            # Try to find a year for this specific root
                            # This is simplified - a more complex parser would link years to specific roots
                            root_year_match = re.search(r'(\d{3,4})', etym_text[:match.start()])
                            root_year = int(root_year_match.group(1)) if root_year_match else None
                            
                            # Create root entry
                            root = {
                                "word": root_word,
                                "language": root_lang,
                                "definition": self.get_brief_definition(root_word, root_lang),
                                "year": root_year if root_year else year,  # Use the main year as fallback
                                "roots": []  # Next level roots would be fetched recursively in a production impl
                            }
                            
                            roots.append(root)
            
            return {
                "word": word,
                "language": language,
                "definition": definition,
                "year": year,
                "roots": roots
            }
        except Exception as e:
            logger.debug(f"EtymOnline lookup failed for {word}: {str(e)}")
            return None

    def fetch_from_freedictionary(self, word: str, language: str) -> Optional[Dict]:
        """Fetch etymology from Free Dictionary API"""
        try:
            lang_code = self.lang_codes.get(language, "en")
            url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang_code}/{word}"
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            # Simplified parsing - real implementation would be more robust
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                meanings = entry.get('meanings', [])
                definition = meanings[0].get('definitions', [{}])[0].get('definition', '') if meanings else ''
                
                # Look for etymology in the entry
                etymology = entry.get('origin', '')
                roots = []
                
                # Try to extract language and root words from etymology text
                if etymology:
                    # Common language patterns
                    language_patterns = {
                        "Latin": [r'Latin[a-z\s]*(\w+)', r'from Latin[a-z\s]*(\w+)'],
                        "Greek": [r'Greek[a-z\s]*(\w+)', r'from Greek[a-z\s]*(\w+)'],
                        "French": [r'French[a-z\s]*(\w+)', r'from French[a-z\s]*(\w+)'],
                    }
                    
                    for root_lang, patterns in language_patterns.items():
                        for pattern in patterns:
                            matches = re.finditer(pattern, etymology)
                            for match in matches:
                                root_word = match.group(1).strip('.,:;')
                                if root_word and root_word != word:  # Avoid self-reference
                                    # Create root entry
                                    root = {
                                        "word": root_word,
                                        "language": root_lang,
                                        "definition": f"Root of {word}",
                                        "year": None,  # Free Dictionary API doesn't typically provide year information
                                        "roots": []
                                    }
                                    
                                    roots.append(root)
                
                etymology_data = {
                    "word": word,
                    "language": language,
                    "definition": definition,
                    "year": None,  # Free Dictionary API typically doesn't provide year information
                    "roots": roots
                }
                
                return etymology_data
            
            return None
        except Exception as e:
            logger.debug(f"Free Dictionary lookup failed for {word}: {str(e)}")
            return None

    def extract_definition(self, data: Dict, language: str) -> str:
        """Extract definition from API response"""
        try:
            lang_code = self.lang_codes.get(language, "en").lower()
            if lang_code in data:
                definitions = data[lang_code]
                if definitions and len(definitions) > 0:
                    definition = definitions[0].get("definitions", [{}])[0].get("definition", "")
                    # Remove HTML tags
                    definition = re.sub(r'<[^>]+>', '', definition)
                    return definition
            return ""
        except:
            return ""

    def process_word(self, word: str, language: str) -> bool:
        """Process a single word and save its etymology data"""
        if word in self.stats["processed_words"]:
            logger.debug(f"Skipping already processed word: {word}")
            return False
            
        try:
            logger.debug(f"Processing {language} word: {word}")
            
            # Fetch etymology data
            etymology_data = self.fetch_etymology(word, language)
            
            if not etymology_data:
                self.stats["failed_words"] += 1
                logger.debug(f"No etymology data found for {word}")
                return False
                
            # Generate file path
            if len(word) > 0:
                first_letter = word[0].lower()
                file_path = self.data_dir / language / first_letter / f"{word}.json"
                
                # Create directory if it doesn't exist
                if not self.test_mode:
                    os.makedirs(file_path.parent, exist_ok=True)
                
                # Save data
                if not self.test_mode:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(etymology_data, f, indent=2)
                
                # Count connections
                root_count = len(etymology_data.get("roots", []))
                self.stats["total_connections"] += root_count
                
                # Update statistics
                self.stats["successful_words"] += 1
                self.stats["languages"][language] = self.stats["languages"].get(language, 0) + 1
                self.stats["last_processed"] = word
                self.stats["processed_words"].add(word)
                
                logger.debug(f"Successfully processed {word} with {root_count} connections")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error processing word {word}: {str(e)}")
            self.stats["failed_words"] += 1
            return False

    def process_batch(self, words: List[str], language: str) -> None:
        """Process a batch of words"""
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.process_word, word, language): word for word in words}
            for future in as_completed(futures):
                word = futures[future]
                try:
                    success = future.result()
                    # Update progress regardless of success
                    self.stats["total_words_processed"] += 1
                except Exception as e:
                    logger.error(f"Exception processing {word}: {str(e)}")
                    self.stats["failed_words"] += 1
                    self.stats["total_words_processed"] += 1

    def estimate_dataset_size(self, word_lists: Dict[str, List[str]]) -> Dict:
        """Estimate the final dataset size based on word lists"""
        total_words = sum(len(words) for words in word_lists.values())
        
        # Assume average of 3 etymology connections per word
        avg_connections_per_word = 3
        total_connections = total_words * avg_connections_per_word
        
        # Assume average JSON file size of 500 bytes
        avg_file_size_bytes = 500
        total_size_bytes = total_words * avg_file_size_bytes
        
        return {
            "total_words": total_words,
            "estimated_connections": total_connections,
            "estimated_size_mb": total_size_bytes / (1024 * 1024),
            "estimated_time_days": total_words / (60 * 24)  # Assuming 60 words per minute
        }

    def run(self):
        """Run the etymology generator"""
        try:
            logger.info(f"Starting etymology generator (test mode: {self.test_mode})")
            
            # Fetch word lists
            word_lists = self.fetch_word_lists()
            
            # Estimate dataset size
            estimates = self.estimate_dataset_size(word_lists)
            logger.info(f"Estimated dataset size: {estimates['estimated_size_mb']:.2f} MB")
            logger.info(f"Estimated total words: {estimates['total_words']}")
            logger.info(f"Estimated total connections: {estimates['estimated_connections']}")
            logger.info(f"Estimated processing time: {estimates['estimated_time_days']:.2f} days")
            
            # Process each language
            for language, words in word_lists.items():
                logger.info(f"Processing {len(words)} {language} words")
                
                # Shuffle words to distribute load more evenly
                random.shuffle(words)
                
                # Process in batches
                for i in tqdm(range(0, len(words), self.batch_size), desc=f"Processing {language} words"):
                    batch = words[i:i+self.batch_size]
                    self.process_batch(batch, language)
                    
                    # Save state periodically
                    if i % (self.batch_size * 10) == 0:
                        self.save_state()
                        
                    # Add small delay between batches to avoid rate limiting
                    time.sleep(1)
            
            # Final state save
            self.save_state()
            
            # Calculate and log statistics
            duration = time.time() - self.stats["start_time"]
            logger.info(f"Completed in {duration/60:.2f} minutes")
            logger.info(f"Total words processed: {self.stats['total_words_processed']}")
            logger.info(f"Successful words: {self.stats['successful_words']}")
            logger.info(f"Failed words: {self.stats['failed_words']}")
            logger.info(f"Total connections: {self.stats['total_connections']}")
            
            return self.stats
            
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            self.save_state()
        except Exception as e:
            logger.error(f"Error running etymology generator: {str(e)}")
            self.save_state()

def main():
    parser = argparse.ArgumentParser(description="Etymology Dataset Generator")
    parser.add_argument("--test", action="store_true", help="Run in test mode (no file writing)")
    parser.add_argument("--threads", type=int, default=1, help="Number of worker threads")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of words to process in each batch")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of words to process per language (0 for no limit)")
    args = parser.parse_args()
    
    generator = EtymologyGenerator(
        test_mode=args.test,
        threads=args.threads,
        batch_size=args.batch_size
    )
    generator.run()

if __name__ == "__main__":
    main() 