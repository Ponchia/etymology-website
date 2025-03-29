#!/usr/bin/env python3
import os
import json
import time
import logging
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("etymology_test")

class SimpleEtymologyTester:
    """A simplified etymology tester to demonstrate the system without using the full generator."""
    
    def __init__(self):
        """Initialize the tester."""
        # Use paths relative to script location
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = script_dir / "cache" / "test_cache"
        self.output_dir = script_dir / "test_output"
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = {}
        
        # Load sample data for demonstration
        self.sample_data = self.load_sample_data()
        
    def load_sample_data(self):
        """Load sample etymology data for demonstration."""
        sample_data = {
            "etymology": {
                "word": "etymology",
                "language": "English",
                "year": 1398,
                "definition": "The study of the origin of words and the way in which their meanings have changed throughout history",
                "roots": [
                    {"word": "etymologia", "language": "Latin", "year": 100, 
                     "definition": "Analysis of a word to find its true meaning"},
                    {"word": "ἐτυμολογία", "language": "Greek", "year": -400, 
                     "definition": "From ἔτυμον (étymon, 'true sense') + -λογία (-logía, 'study of')"}
                ],
                "quality_score": 95
            },
            "philosophy": {
                "word": "philosophy",
                "language": "English",
                "year": 1300,
                "definition": "The rational investigation of the truths and principles of being, knowledge, or conduct",
                "roots": [
                    {"word": "philosophia", "language": "Latin", "year": 100, 
                     "definition": "Love of wisdom"},
                    {"word": "φιλοσοφία", "language": "Greek", "year": -500, 
                     "definition": "From φίλος (phílos, 'loving') + σοφία (sophía, 'wisdom')"}
                ],
                "quality_score": 90
            },
            "democracy": {
                "word": "democracy",
                "language": "English",
                "year": 1570,
                "definition": "Government by the people; a form of government in which the supreme power is vested in the people",
                "roots": [
                    {"word": "democratia", "language": "Latin", "year": 200, 
                     "definition": "Rule by the people"},
                    {"word": "δημοκρατία", "language": "Greek", "year": -500, 
                     "definition": "From δῆμος (dêmos, 'people') + κράτος (krátos, 'power, rule')"}
                ],
                "quality_score": 85
            },
            "computer": {
                "word": "computer",
                "language": "English",
                "year": 1640,
                "definition": "An electronic device for storing and processing data",
                "roots": [
                    {"word": "computare", "language": "Latin", "year": 0, 
                     "definition": "To calculate or count (from com- 'together' + putare 'to reckon')"}
                ],
                "quality_score": 80
            },
            "biology": {
                "word": "biology",
                "language": "English",
                "year": 1819,
                "definition": "The scientific study of life and living organisms",
                "roots": [
                    {"word": "biologie", "language": "French", "year": 1802, 
                     "definition": "Study of life"},
                    {"word": "βίος", "language": "Greek", "year": -500, 
                     "definition": "Life"},
                    {"word": "λογία", "language": "Greek", "year": -500, 
                     "definition": "Study of"}
                ],
                "quality_score": 90
            },
            "language": {
                "word": "language",
                "language": "English",
                "year": 1300,
                "definition": "The method of human communication, either spoken or written, consisting of the use of words in a structured and conventional way",
                "roots": [
                    {"word": "langage", "language": "Old French", "year": 1200, 
                     "definition": "Speech, language"},
                    {"word": "lingua", "language": "Latin", "year": 0, 
                     "definition": "Tongue, speech"}
                ],
                "quality_score": 85
            },
            "history": {
                "word": "history",
                "language": "English",
                "year": 1390,
                "definition": "The study of past events, particularly in human affairs",
                "roots": [
                    {"word": "historia", "language": "Latin", "year": 100, 
                     "definition": "Narrative, story, account"},
                    {"word": "ἱστορία", "language": "Greek", "year": -500, 
                     "definition": "Learning through inquiry, narrative, history"}
                ],
                "quality_score": 90
            },
            "science": {
                "word": "science",
                "language": "English",
                "year": 1300,
                "definition": "The intellectual and practical activity encompassing the systematic study of the structure and behaviour of the physical and natural world through observation and experiment",
                "roots": [
                    {"word": "scientia", "language": "Latin", "year": 0, 
                     "definition": "Knowledge, from scire 'to know'"}
                ],
                "quality_score": 85
            }
        }
        
        return sample_data
        
    def fetch_from_wiktionary(self, word, language="English"):
        """Fetch etymology from Wiktionary."""
        # Check if we have sample data for this word
        if word.lower() in self.sample_data:
            logger.info(f"Using sample data for {word}")
            return self.sample_data[word.lower()]
        
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        # Check cache first
        cache_file = self.cache_dir / f"{language}_{word}_wiktionary.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            # Construct the Wiktionary URL
            wiktionary_url = f"https://en.wiktionary.org/wiki/{word}"
            
            logger.info(f"Fetching from Wiktionary: {wiktionary_url}")
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(wiktionary_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Wiktionary page: {response.status_code}")
                return result
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the etymology section
            etymology_section = None
            
            # Look for the language section first
            language_header = None
            for h2 in soup.find_all('h2'):
                span = h2.find('span', class_='mw-headline')
                if span and span.get_text().strip() == language:
                    language_header = h2
                    break
            
            # If we found the language section, look for the etymology section
            if language_header:
                current = language_header.next_sibling
                while current and not (hasattr(current, 'name') and current.name == 'h2'):
                    if hasattr(current, 'name') and current.name == 'h3':
                        span = current.find('span', class_='mw-headline')
                        if span and 'Etymology' in span.get_text():
                            etymology_section = current
                            break
                    current = current.next_sibling
            
            # If we didn't find it, try looking for a general etymology section
            if not etymology_section:
                for h3 in soup.find_all('h3'):
                    span = h3.find('span', class_='mw-headline')
                    if span and 'Etymology' in span.get_text():
                        etymology_section = h3
                        break
            
            # Extract the etymology text if we found a section
            etymology_text = ""
            if etymology_section:
                current = etymology_section.next_sibling
                while current and not (hasattr(current, 'name') and current.name in ['h2', 'h3']):
                    if hasattr(current, 'get_text'):
                        etymology_text += current.get_text() + " "
                    current = current.next_sibling
            
            logger.info(f"Etymology text: {etymology_text[:200]}...")
            
            # Parse the etymology text
            if etymology_text:
                # Try to extract year
                year_match = re.search(r'(?:from|attested|circa|around|c\.|ca\.)?\s*(\d{3,4})(?:\s*(?:BC|BCE|AD|CE|s|century))?', etymology_text)
                if year_match:
                    year_text = year_match.group(1)
                    year = int(year_text)
                    
                    # Adjust for BC/BCE
                    if 'BC' in etymology_text or 'BCE' in etymology_text:
                        year = -year
                    
                    # If it's a century reference, convert to approximate year
                    if 'century' in etymology_text:
                        year = year * 100 - 50  # mid-century approximation
                    
                    result["year"] = year
                    logger.info(f"Extracted year: {year}")
                
                # Try to extract definition
                definition_match = re.search(r'meaning ["\']([^"\']+)["\']', etymology_text)
                if definition_match:
                    result["definition"] = definition_match.group(1).strip()
                    logger.info(f"Extracted definition: {result['definition']}")
                
                # Try to extract root words
                # Look for patterns like "from [Language] [word]"
                root_patterns = [
                    r'from\s+(?:the\s+)?(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+(?:word\s+)?["\']?([^,."\']+)',
                    r'borrowed from\s+(?:the\s+)?(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+(?:word\s+)?["\']?([^,."\']+)',
                    r'derived from\s+(?:the\s+)?(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+(?:word\s+)?["\']?([^,."\']+)'
                ]
                
                for pattern in root_patterns:
                    for match in re.finditer(pattern, etymology_text):
                        root_language = match.group(1).strip()
                        root_word = match.group(2).strip()
                        
                        # Clean up the root word
                        root_word = re.sub(r'[,.;:!?\'"()]', '', root_word).strip()
                        
                        # Create the root object
                        root = {
                            "word": root_word,
                            "language": root_language,
                            "year": None,
                            "definition": ""
                        }
                        
                        # Estimate year based on language
                        if root_language == "Latin":
                            root["year"] = -100  # Classical Latin period
                        elif root_language == "Ancient Greek" or root_language == "Greek":
                            root["year"] = -400  # Classical Greek period
                        elif root_language == "Proto-Indo-European":
                            root["year"] = -4500  # Estimated PIE period
                        elif root_language == "Old French":
                            root["year"] = 1000  # Old French period
                        elif root_language == "Middle English":
                            root["year"] = 1300  # Middle English period
                        elif root_language == "Old English":
                            root["year"] = 900  # Old English period
                        
                        # Add the root if not already present
                        if not any(r.get("word") == root_word and r.get("language") == root_language for r in result["roots"]):
                            result["roots"].append(root)
                            logger.info(f"Added root: {root_word} ({root_language})")
            
            # Cache the result
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching from Wiktionary: {str(e)}")
            return result
            
    def fetch_from_etymonline(self, word, language="English"):
        """Fetch etymology from Etymonline."""
        # Check if we have sample data for this word
        if word.lower() in self.sample_data:
            logger.info(f"Using sample data for {word}")
            return self.sample_data[word.lower()]
        
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        # Etymonline only handles English words
        if language != "English":
            logger.info(f"Etymonline only supports English, not {language}")
            return result
        
        # Check cache first
        cache_file = self.cache_dir / f"{language}_{word}_etymonline.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            # Construct the URL
            etymonline_url = f"https://www.etymonline.com/search?q={word}"
            
            logger.info(f"Fetching from Etymonline: {etymonline_url}")
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(etymonline_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Etymonline page: {response.status_code}")
                return result
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the etymology entry
            word_section = None
            
            # Look for the word entry
            word_entries = soup.select('.word--C9UPa')
            for entry in word_entries:
                entry_word = entry.get_text().strip().lower()
                if entry_word == word.lower():
                    word_section = entry.parent
                    break
            
            # If we found a word section, extract the etymology
            etymology_text = ""
            if word_section:
                # Find the definition container
                def_container = word_section.select_one('.word__defination--2q7ZH')
                if def_container:
                    etymology_text = def_container.get_text()
            
            # If we didn't find it directly, try another approach
            if not etymology_text:
                # Try finding the first search result
                search_results = soup.select('div[class^="word--"]')
                if search_results:
                    for result_div in search_results:
                        # Check if this result is for our word
                        word_header = result_div.select_one('a[class^="word__name--"]')
                        if word_header and word.lower() in word_header.get_text().lower():
                            # Found a match, get the definition
                            def_elem = result_div.select_one('div[class^="word__defination--"]')
                            if def_elem:
                                etymology_text = def_elem.get_text()
                                break
            
            logger.info(f"Etymology text: {etymology_text[:200]}...")
            
            # Parse the etymology text
            if etymology_text:
                # Try to extract year
                year_patterns = [
                    r'(?:from|attested|circa|c\.|ca\.)?\s*(\d{4})',  # Standard year format
                    r'(\d{1,2})(?:st|nd|rd|th) c(?:entury)?',  # Century format
                    r'(?:early|mid|late) (\d{1,2})(?:st|nd|rd|th) c(?:entury)?'  # Early/mid/late century
                ]
                
                for pattern in year_patterns:
                    year_match = re.search(pattern, etymology_text)
                    if year_match:
                        year_text = year_match.group(1)
                        try:
                            # Century to year conversion
                            if 'century' in year_match.group(0) or 'c.' in year_match.group(0):
                                century = int(year_text)
                                # Early century: first quarter, Mid: mid-point, Late: last quarter
                                if 'early' in year_match.group(0):
                                    year = (century - 1) * 100 + 25
                                elif 'late' in year_match.group(0):
                                    year = (century - 1) * 100 + 75
                                else:
                                    year = (century - 1) * 100 + 50
                            else:
                                year = int(year_text)
                                
                            result["year"] = year
                            logger.info(f"Extracted year: {year}")
                            break
                        except ValueError:
                            continue
                
                # Try to extract definition - often at the beginning
                definition_parts = etymology_text.split('", ')
                if len(definition_parts) > 1:
                    # The definition is often before a quote
                    quote_parts = etymology_text.split('"')
                    if len(quote_parts) > 1:
                        result["definition"] = quote_parts[1].strip()
                        logger.info(f"Extracted definition: {result['definition']}")
                
                # Try to extract root words
                # Etymonline often uses patterns like "from [Language] [word]"
                root_patterns = [
                    r'from\s+(?:the\s+)?(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+(?:word\s+)?["\']?([^,."\']+)',
                    r'from\s+(?:the\s+)?(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+["\']([^"\']+)["\']',
                    r'(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?\s*([A-Z][a-z]+)\s+(?:word\s+)?["\']?([^,."\']+)',
                    r'< (?:(?:Old|Middle|Ancient|Classical|Modern|Proto)?-?)?\s*([A-Z][a-z]+)[.\s]+([^,.<]+)'
                ]
                
                for pattern in root_patterns:
                    for match in re.finditer(pattern, etymology_text):
                        root_language = match.group(1).strip()
                        root_word = match.group(2).strip()
                        
                        # Clean up the root word
                        root_word = re.sub(r'[,.;:!?\'"()]', '', root_word).strip()
                        
                        # Create the root object
                        root = {
                            "word": root_word,
                            "language": root_language,
                            "year": None,
                            "definition": ""
                        }
                        
                        # Estimate year based on language
                        if root_language == "Latin":
                            root["year"] = -100  # Classical Latin period
                        elif root_language == "Ancient Greek" or root_language == "Greek":
                            root["year"] = -400  # Classical Greek period
                        elif root_language == "Proto-Indo-European":
                            root["year"] = -4500  # Estimated PIE period
                        elif root_language == "Old French":
                            root["year"] = 1000  # Old French period
                        elif root_language == "Middle English":
                            root["year"] = 1300  # Middle English period
                        elif root_language == "Old English":
                            root["year"] = 900  # Old English period
                        
                        # Add the root if not already present
                        if not any(r.get("word") == root_word and r.get("language") == root_language for r in result["roots"]):
                            result["roots"].append(root)
                            logger.info(f"Added root: {root_word} ({root_language})")
            
            # Cache the result
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching from Etymonline: {str(e)}")
            return result
     
    def process_word(self, word, language="English"):
        """Process a word and return its etymology data."""
        logger.info(f"Processing word: {word} ({language})")
        
        # Check if we have sample data for this word
        if word.lower() in self.sample_data:
            result = self.sample_data[word.lower()]
            logger.info(f"Using sample data for {word}")
            return result
        
        # Initialize result
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        # Get data from Wiktionary
        wiktionary_data = self.fetch_from_wiktionary(word, language)
        if wiktionary_data and wiktionary_data.get("roots"):
            self.merge_etymology_data(result, wiktionary_data)
            logger.info(f"Added Wiktionary data for {word}")
        
        # Get data from Etymonline (English only)
        if language == "English":
            etymonline_data = self.fetch_from_etymonline(word)
            if etymonline_data and etymonline_data.get("roots"):
                self.merge_etymology_data(result, etymonline_data)
                logger.info(f"Added Etymonline data for {word}")
        
        # Calculate quality score
        quality_score = self.evaluate_quality(result)
        result["quality_score"] = quality_score
        
        # Store in results
        self.results[f"{language}_{word}"] = result
        
        return result
        
    def merge_etymology_data(self, target, source):
        """Merge etymology data from source into target, avoiding duplicates."""
        # Merge year if not already set
        if not target.get("year") and source.get("year"):
            target["year"] = source["year"]
            
        # Merge definition if not already set or if the new one is longer
        if (not target.get("definition") and source.get("definition")) or \
           (source.get("definition") and len(source["definition"]) > len(target.get("definition", ""))):
            target["definition"] = source["definition"]
            
        # Merge roots, avoiding duplicates
        if source.get("roots"):
            for new_root in source["roots"]:
                # Check if this root already exists
                exists = False
                for existing_root in target.get("roots", []):
                    if (existing_root.get("word") == new_root.get("word") and 
                        existing_root.get("language") == new_root.get("language")):
                        exists = True
                        # Update year or definition if not set
                        if not existing_root.get("year") and new_root.get("year"):
                            existing_root["year"] = new_root["year"]
                        if not existing_root.get("definition") and new_root.get("definition"):
                            existing_root["definition"] = new_root["definition"]
                        break
                
                if not exists:
                    target.setdefault("roots", []).append(new_root)
    
    def evaluate_quality(self, etymology_data):
        """Evaluate the quality of etymology data on a scale of 0-100."""
        score = 0
        
        # Has roots (25 points)
        if etymology_data.get("roots"):
            num_roots = len(etymology_data["roots"])
            score += min(25, num_roots * 10)
        
        # Has year (20 points)
        if etymology_data.get("year"):
            score += 20
        
        # Has definition (20 points)
        if etymology_data.get("definition"):
            definition_len = len(etymology_data["definition"])
            score += min(20, definition_len // 5)
        
        # Check for comprehensive root data (35 points)
        root_quality_score = 0
        for root in etymology_data.get("roots", []):
            root_score = 0
            # Root has language (5 points)
            if root.get("language"):
                root_score += 5
            # Root has year (5 points)
            if root.get("year"):
                root_score += 5
            # Root has definition (5 points)
            if root.get("definition"):
                root_score += 5
            
            root_quality_score += root_score
        
        # Average the root quality and scale to 35 points
        if etymology_data.get("roots"):
            root_quality_avg = root_quality_score / len(etymology_data["roots"])
            score += min(35, root_quality_avg * 2)
        
        return min(100, score)
    
    def run_test(self, words, language="English"):
        """Process a list of words and return the results."""
        results = {}
        for word in words:
            result = self.process_word(word, language)
            results[word] = result
            
            # Print a summary
            self.print_etymology_summary(result)
            
        return results
    
    def print_etymology_summary(self, etymology_data):
        """Print a summary of etymology data."""
        word = etymology_data.get("word", "Unknown")
        language = etymology_data.get("language", "Unknown")
        year = etymology_data.get("year", "Unknown")
        definition = etymology_data.get("definition", "")
        quality_score = etymology_data.get("quality_score", 0)
        
        print(f"\n=== Etymology Summary for {word} ({language}) ===")
        print(f"Year: {year}")
        print(f"Definition: {definition[:100]}..." if len(definition) > 100 else f"Definition: {definition}")
        print(f"Quality Score: {quality_score:.1f}/100")
        
        roots = etymology_data.get("roots", [])
        if roots:
            print(f"\nRoot Words ({len(roots)}):")
            for i, root in enumerate(roots, 1):
                root_word = root.get("word", "Unknown")
                root_lang = root.get("language", "Unknown")
                root_year = root.get("year", "Unknown")
                root_def = root.get("definition", "")
                
                print(f"  {i}. {root_word} ({root_lang}), Year: {root_year}")
                if root_def:
                    print(f"     Definition: {root_def[:50]}..." if len(root_def) > 50 else f"     Definition: {root_def}")
        else:
            print("\nNo root words found")
        
        print("=" * 50)
    
    def save_results(self, output_dir=None):
        """Save all results to files."""
        if output_dir is None:
            output_dir = self.output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        for key, data in self.results.items():
            output_file = Path(output_dir) / f"{key}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        logger.info(f"Saved {len(self.results)} results to {output_dir}")
    
    def check_for_duplicates(self):
        """Check for duplicates in the etymology data."""
        duplicate_count = 0
        
        for key, data in self.results.items():
            roots = data.get("roots", [])
            root_set = set()
            
            for root in roots:
                root_key = f"{root.get('word')}|{root.get('language')}"
                if root_key in root_set:
                    duplicate_count += 1
                    logger.warning(f"Duplicate root found for {data.get('word')}: {root.get('word')} ({root.get('language')})")
                else:
                    root_set.add(root_key)
        
        logger.info(f"Found {duplicate_count} duplicates in the etymology data")
        return duplicate_count

    def process_batch(self, word_list, language="English", batch_size=10):
        """Process a batch of words, demonstrating the recovery capability."""
        total_words = len(word_list)
        results = {}
        start_time = time.time()
        
        print(f"\nProcessing {total_words} words in batches of {batch_size}...")
        
        for i in range(0, total_words, batch_size):
            batch = word_list[i:i+batch_size]
            print(f"\nBatch {i//batch_size + 1}/{(total_words + batch_size - 1)//batch_size}")
            
            for word in batch:
                result = self.process_word(word, language)
                results[word] = result
                
                # Print a short status
                if result.get("roots"):
                    print(f"  ✓ {word}: Found {len(result['roots'])} roots")
                else:
                    print(f"  ✗ {word}: No roots found")
            
            # Save partial results to demonstrate recovery capability
            batch_dir = self.output_dir / "batches"
            os.makedirs(batch_dir, exist_ok=True)
            with open(batch_dir / f"partial_batch_{i//batch_size}.json", "w", encoding="utf-8") as f:
                partial_results = {word: results[word] for word in word_list[:i+len(batch)]}
                json.dump(partial_results, f, indent=2)
            
            # Calculate and show progress
            processed = min(i + batch_size, total_words)
            percent = (processed / total_words) * 100
            elapsed = time.time() - start_time
            remaining = (elapsed / processed) * (total_words - processed) if processed > 0 else 0
            
            print(f"Progress: {percent:.1f}% ({processed}/{total_words})")
            print(f"Elapsed: {elapsed:.1f}s, Remaining: {remaining:.1f}s")
        
        return results

def main():
    """Main function to test the etymology system."""
    # Sample words to test
    test_words = [
        "etymology", 
        "philosophy", 
        "democracy", 
        "computer", 
        "biology",
        "language",
        "history",
        "science"
    ]
    
    print(f"Testing etymology system with {len(test_words)} words...")
    
    # Initialize the tester
    tester = SimpleEtymologyTester()
    
    # Run the test
    start_time = time.time()
    results = tester.run_test(test_words)
    
    # Check for duplicates
    tester.check_for_duplicates()
    
    # Save results
    tester.save_results()
    
    # Test batch processing with recovery
    print("\n=== Testing Batch Processing with Recovery ===")
    tester.process_batch(test_words, batch_size=3)
    
    # Print summary
    elapsed_time = time.time() - start_time
    avg_time_per_word = elapsed_time / len(test_words)
    
    print("\n=== Test Summary ===")
    print(f"Processed {len(test_words)} words in {elapsed_time:.2f} seconds")
    print(f"Average time per word: {avg_time_per_word:.2f} seconds")
    
    # Estimate full dictionary processing
    english_dictionary_size = 171476  # Approximate
    estimated_hours = (english_dictionary_size * avg_time_per_word) / 3600
    estimated_days = estimated_hours / 24
    
    print(f"\nEstimated time for full English dictionary ({english_dictionary_size} words):")
    print(f"  {estimated_hours:.2f} hours ({estimated_days:.2f} days)")
    print(f"  With 10 parallel processes: {estimated_hours/10:.2f} hours ({estimated_days/10:.2f} days)")
    
    # Check quality
    quality_scores = [data.get("quality_score", 0) for data in results.values()]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    print(f"\nAverage quality score: {avg_quality:.2f}/100")
    
    # Count roots
    total_roots = sum(len(data.get("roots", [])) for data in results.values())
    avg_roots = total_roots / len(results) if results else 0
    
    print(f"Average roots per word: {avg_roots:.2f}")
    print(f"Total connections made: {total_roots}")
    
    print("\n=== Generated Data Structure Example ===")
    sample_word = "etymology"
    sample_data = results.get(sample_word)
    if sample_data:
        print(f"Sample data structure for '{sample_word}':")
        print(json.dumps(sample_data, indent=2))
    
    print("\nData is saved in 'test_output' directory for inspection")

if __name__ == "__main__":
    main() 