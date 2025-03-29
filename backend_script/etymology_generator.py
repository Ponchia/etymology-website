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
    def __init__(self, max_words=None, languages=None, test_mode=False):
        """Initialize the etymology generator."""
        # Basic setup and logging configuration
        self.test_mode = test_mode
        self.logger = logging.getLogger("etymology_generator")
        
        # Configure output files and directories
        self.output_dir = self.setup_output_directory()
        
        # Initialize language detection and NLP tools
        self.initialize_language_detection()
        
        # Keep track of progress 
        self.words_processed = 0
        self.connections_made = 0
        self.successful_words = 0
        self.failed_words = 0
        
        # Languages to process
        self.languages = languages if languages else ["English", "French", "German"]
        
        # Maximum number of words to process
        self.max_words = max_words
        
        # For testing
        self.results = {}
        
        # Load supplementary data
        self.supplementary_data = self.load_supplementary_data()
        
        self.logger.info(f"Starting etymology generator (test mode: {test_mode})")

    def setup_output_directory(self):
        """Set up the output directory for storing etymology data."""
        output_dir = Path("./output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

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

    def fetch_etymology(self, word, language="English"):
        """
        Fetch etymology for a word using multiple sources.
        Returns a dictionary with etymology information.
        """
        word = word.lower().strip()
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": [],
            "etymology": []
        }
        
        try:
            # First check if we have high-quality supplementary data
            supplementary_key = word.lower()
            if supplementary_key in self.supplementary_data:
                self.logger.info(f"Using supplementary data for {word}")
                supp_data = self.supplementary_data[supplementary_key]
                
                # Transfer data from supplementary source
                result["year"] = supp_data.get("year")
                result["language"] = supp_data.get("language", language)
                
                # Add roots from supplementary data
                if "roots" in supp_data:
                    result["roots"] = supp_data["roots"]
                    # Also use the same for etymology for consistency
                    result["etymology"] = supp_data["roots"]
                    
                    # Log successful use of supplementary data
                    self.logger.debug(f"Added {len(result['roots'])} roots from supplementary data for {word}")
                    return result
            
            # If no supplementary data, try Wiktionary first
            self.logger.debug(f"Fetching etymology for {word} ({language}) from Wiktionary")
            wiktionary_result = self.fetch_from_wiktionary(word, language)
            
            if wiktionary_result["roots"] or wiktionary_result["year"]:
                # Use Wiktionary if it provided useful information
                result.update(wiktionary_result)
            else:
                # Fall back to EtymOnline for English
                if language == "English":
                    self.logger.debug(f"Falling back to EtymOnline for {word}")
                    etymonline_result = self.fetch_from_etymonline(word)
                    if etymonline_result["roots"] or etymonline_result["year"]:
                        result.update(etymonline_result)
                # Try Free Dictionary as a last resort
                if not result["roots"] and not result["year"]:
                    self.logger.debug(f"Trying Free Dictionary for {word}")
                    freedict_result = self.fetch_from_freedictionary(word, language)
                    if freedict_result["definition"] or freedict_result["roots"]:
                        result.update(freedict_result)
                        
            # Ensure we have at least a definition
            if not result["definition"] and language == "English":
                # Try dictionary API if we don't have a definition yet
                self.logger.debug(f"Fetching definition for {word}")
                definition = self.fetch_definition(word)
                if definition:
                    result["definition"] = definition
                                    
            return result
        
        except Exception as e:
            self.logger.error(f"Error fetching etymology for {word}: {str(e)}")
            return result

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
            if "parse" not in data or "text" not in data["parse"]:
                return []
                
            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the etymology section
            etymology_section = None
            
            # Look for etymology section header
            etym_headers = soup.find_all(['h3', 'h4'], class_=lambda c: c and 'etymology' in c.lower())
            if not etym_headers:
                etym_headers = soup.find_all(['h3', 'h4'], string=lambda s: s and 'etymology' in s.lower())
            
            if etym_headers:
                etymology_section = etym_headers[0].find_next('p')
            
            # If we couldn't find a dedicated etymology section, look for etymology information
            # in the language section
            if not etymology_section:
                lang_headers = soup.find_all(['h2', 'h3', 'h4'], id=lambda i: i and language.lower() in i.lower())
                if lang_headers:
                    # Look through all paragraphs in this section
                    for p in lang_headers[0].find_next_siblings('p'):
                        if p.text and any(x in p.text.lower() for x in ['from', 'derive', 'origin', 'etymo']):
                            etymology_section = p
                            break

            if not etymology_section:
                return []

            etymology_text = etymology_section.text
            
            # Extract origins
            roots = []
            
            # Fix language tagging in patterns
            language_prefixes = {
                "Ancient Greek": ["Ancient Greek", "Ancient"],
                "Latin": ["Latin", "Classical Latin"],
                "Old French": ["Old French", "Old"],
                "Middle English": ["Middle English"],
                "Proto-Germanic": ["Proto-Germanic"],
                "Proto-Indo-European": ["Proto-Indo-European", "PIE"],
                "Greek": ["Greek"],
                "French": ["French"],
                "German": ["German"],
                "Sanskrit": ["Sanskrit"]
            }
            
            # Create a mapping of prefixes to their canonical language names
            prefix_to_language = {}
            for lang, prefixes in language_prefixes.items():
                for prefix in prefixes:
                    prefix_to_language[prefix] = lang
            
            # Define patterns for common etymology phrases
            patterns = [
                r'from\s+([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)\s+["\']?([^,"\']+)["\']?',  # from Latin "exemplum"
                r'from\s+([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)\s+(?:word|term)?\s*["\']?([^,"\']+)["\']?',  # from Latin word "exemplum"
                r'([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)\s+(?:word|origin)?\s*["\']?([^,"\']+)["\']?',  # Latin "exemplum"
                r'derived\s+from\s+(?:the\s+)?([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)\s+["\']?([^,"\']+)["\']?',  # derived from the Latin "exemplum"
                r'borrowed\s+from\s+(?:the\s+)?([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)\s+["\']?([^,"\']+)["\']?',  # borrowed from Latin "exemplum"
            ]
            
            # Look for year patterns 
            year_patterns = [
                r'\b(\d{3,4})s?\b',  # Basic year like 1200 or 1200s
                r'\bcirca\s+(\d{3,4})\b',  # circa 1200
                r'\bc\.\s*(\d{3,4})\b',  # c. 1200
                r'\b(\d{3,4})\s+[A-Z]',  # Year followed by capitalized word (likely CE/BCE/AD/BC)
                r'\bfirst\s+recorded\s+in\s+(\d{3,4})\b',  # first recorded in 1200
                r'\bfirst\s+attested\s+in\s+(\d{3,4})\b',  # first attested in 1200
                r'\bearly\s+(\d{2})(?:th|st|nd|rd)\s+century\b',  # early 12th century
                r'\blate\s+(\d{2})(?:th|st|nd|rd)\s+century\b'  # late 12th century
            ]
            
            # Extract year if available
            etymology_year = None
            for pattern in year_patterns:
                year_match = re.search(pattern, etymology_text)
                if year_match:
                    try:
                        year_str = year_match.group(1)
                        # Handle century format (e.g., "12th century" -> 1200)
                        if len(year_str) == 2 and "century" in etymology_text[year_match.start():year_match.end()+10]:
                            # If "late century", add 50 years
                            if "late" in etymology_text[max(0, year_match.start()-10):year_match.start()]:
                                etymology_year = int(year_str) * 100 + 50
                            else:
                                etymology_year = int(year_str) * 100
                        else:
                            etymology_year = int(year_str)
                        break
                    except ValueError:
                        pass
            
            for pattern in patterns:
                matches = re.findall(pattern, etymology_text)
                for match in matches:
                    origin_language_raw = match[0].strip()
                    origin_word = match[1].strip()
                    
                    # Normalize language name
                    origin_language = None
                    for prefix, lang in prefix_to_language.items():
                        if origin_language_raw.startswith(prefix):
                            origin_language = lang
                            break
                    
                    # If not found in our mapping, use as is
                    if not origin_language:
                        # Skip if it doesn't look like a language name
                        if origin_language_raw.lower() in ["from", "by", "and", "the", "see", "this"]:
                            continue
                        origin_language = origin_language_raw
                    
                    # Clean up phrases that aren't actually language names
                    if any(phrase in origin_language.lower() for phrase in ["from", "borrowed", "english from", "english by"]):
                        continue
                    
                    # Skip if any of these terms appear in the supposed etymology
                    skip_terms = ['see also', 'plural', 'and', 'third-person', 'present', 'WordNet', 'singular', 'verb form']
                    if any(term in origin_word.lower() for term in skip_terms) or \
                       any(term in origin_language_raw.lower() for term in skip_terms):
                        continue
                    
                    # Skip if the origin word is significantly longer than typical words (likely a phrase)
                    if len(origin_word.split()) > 3:
                        continue
                    
                    # Extract word from format that might include transliteration
                    # Example: "Greek κόσμος (kósmos)" -> word: "κόσμος", transliteration: "kósmos"
                    transliteration = None
                    transliteration_match = re.search(r'([^\s]+)\s+\(([^)]+)\)', origin_word)
                    if transliteration_match:
                        try:
                            clean_word = transliteration_match.group(1)
                            transliteration = transliteration_match.group(2)
                            origin_word = clean_word
                        except IndexError:
                            pass
                    
                    # Create root entry if it doesn't duplicate an existing one
                    if not any(r.get('word') == origin_word and r.get('language') == origin_language for r in roots):
                        root_entry = {
                            "word": origin_word,
                            "language": origin_language,
                            "definition": f"Origin of {word}",
                            "year": etymology_year,
                            "roots": []
                        }
                        
                        # Add transliteration if available
                        if transliteration:
                            root_entry["transliteration"] = transliteration
                            
                        roots.append(root_entry)
            
            # Clean up special cases
            cleaned_roots = []
            for root in roots:
                # Fix language assignment errors - typically "From X" is not a language
                lang = root.get("language", "")
                if lang.startswith("From "):
                    # Try to extract language from this format
                    lang_parts = lang.split()
                    if len(lang_parts) > 1 and lang_parts[1][0].isupper():
                        root["language"] = lang_parts[1]
                        
                # Only include roots with reasonable language names
                if root.get("language") in language_prefixes or root.get("language") in [
                    "Proto-Germanic", "Latin", "Greek", "French", "German", "Italian", "Spanish",
                    "Old English", "Middle English", "Old Norse", "Sanskrit", "Arabic"
                ]:
                    cleaned_roots.append(root)
                else:
                    # Try the fallback
                    if "From" in root.get("language", ""):
                        continue
                    # If seems like a valid language name (capitalized, not a common word)
                    if root.get("language", "")[0].isupper() and not any(x in root.get("language", "").lower() for x in ["see", "the", "and", "by", "from"]):
                        cleaned_roots.append(root)
            
            return cleaned_roots
        except Exception as e:
            logger.error(f"Error extracting etymology roots: {str(e)}")
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
        """Fetch etymology from Etymonline"""
        try:
            url = f"https://www.etymonline.com/word/{word}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the main etymology section
            etymology_section = soup.select_one('section.word__defination')
            if not etymology_section:
                return None
                
            # Get the word's definition/description
            definition = ""
            definition_p = etymology_section.select_one('p')
            if definition_p:
                definition = definition_p.text.strip()
                
            # Extract year
            year = None
            year_match = re.search(r'\((\d{3,4})(?:s?)\)', definition)
            if year_match:
                try:
                    year = int(year_match.group(1))
                except ValueError:
                    pass
                    
            # Parse etymology text for origin words
            roots = []
            
            # Look for language origins patterns like "from Latin exemplum"
            languages = {
                'Latin': ['Latin'],
                'Greek': ['Greek', 'Ancient Greek'],
                'French': ['French', 'Old French'],
                'Old English': ['Old English'],
                'Middle English': ['Middle English'], 
                'German': ['German', 'Old German', 'Middle High German'],
                'Spanish': ['Spanish'],
                'Italian': ['Italian'],
                'Proto-Germanic': ['Proto-Germanic', 'P.Gmc.'],
                'Proto-Indo-European': ['Proto-Indo-European', 'PIE', 'PIE root'],
                'Sanskrit': ['Sanskrit'],
                'Arabic': ['Arabic']
            }
            
            # Flatten the language map for regex pattern
            all_language_patterns = []
            for primary_lang, variants in languages.items():
                for variant in variants:
                    all_language_patterns.append(variant)
            
            # Different patterns to match etymology statements
            etymology_patterns = [
                rf'from\s+({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                rf'({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                rf'borrowed\s+from\s+({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                rf'from\s+({"|".join(all_language_patterns)})\s+(?:word|root|stem)\s+["\']?(\w+)["\']?'
            ]
            
            # Map from variant to primary language
            variant_to_primary = {}
            for primary, variants in languages.items():
                for variant in variants:
                    variant_to_primary[variant] = primary
            
            for pattern in etymology_patterns:
                matches = re.findall(pattern, definition)
                for match in matches:
                    variant_lang, word_origin = match
                    
                    # Map the variant to primary language
                    primary_lang = variant_to_primary.get(variant_lang, variant_lang)
                    
                    if not any(r.get('word') == word_origin and r.get('language') == primary_lang for r in roots):
                        # Get approximate time period for this root if available
                        root_year = None
                        if year and primary_lang == 'Latin':
                            # Approximate Latin period before English adoption
                            root_year = year - 500 if year > 1000 else year - 200
                        elif year and primary_lang == 'Greek':
                            # Approximate Greek period before English adoption
                            root_year = year - 800 if year > 1200 else year - 300
                        elif year and 'Proto' in primary_lang:
                            # Approximate Proto-language period
                            root_year = year - 1500
                            
                        roots.append({
                            "word": word_origin,
                            "language": primary_lang,
                            "definition": f"Origin of {word}",
                            "year": root_year,
                            "roots": []
                        })
            
            if not roots and definition:
                # Try more general patterns if specific ones didn't work
                general_patterns = [
                    r'from\s+(\w+)\s+["\']?(\w+)["\']?',  # from X "Y"
                    r'cognate\s+with\s+(\w+)\s+["\']?(\w+)["\']?',  # cognate with X "Y"
                ]
                
                for pattern in general_patterns:
                    matches = re.findall(pattern, definition)
                    for match in matches:
                        lang, word_origin = match
                        
                        # Skip common words mistaken for languages
                        skip_words = ['the', 'and', 'also', 'see', 'its', 'this', 'other', 'with', 'from']
                        if lang.lower() in skip_words or len(lang) < 3:
                            continue
                        
                        # Check if this looks like a language name (capitalized)
                        if not lang[0].isupper():
                            continue
                            
                        if not any(r.get('word') == word_origin and r.get('language') == lang for r in roots):
                            roots.append({
                                "word": word_origin,
                                "language": lang,
                                "definition": f"Origin of {word}",
                                "year": None,
                                "roots": []
                            })
            
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
        """Fetch data from The Free Dictionary API"""
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/{self.lang_codes.get(language, 'en')}/{word}"
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if not data or not isinstance(data, list) or not data[0]:
                return None
                
            entry = data[0]
            
            # Extract definition
            definition = ""
            if "meanings" in entry and entry["meanings"]:
                for meaning in entry["meanings"]:
                    if "definitions" in meaning and meaning["definitions"]:
                        definition = meaning["definitions"][0].get("definition", "")
                        if definition:
                            break
            
            if not definition and "phonetics" in entry and entry["phonetics"]:
                for phonetic in entry["phonetics"]:
                    if "text" in phonetic and phonetic["text"]:
                        definition = f"Pronunciation: {phonetic['text']}"
                        break
            
            # Look for etymology information
            etymology_text = ""
            if "origin" in entry and entry["origin"]:
                etymology_text = entry["origin"]
            elif "etymologies" in entry and entry["etymologies"]:
                etymology_text = " ".join(entry["etymologies"])
                
            # Extract roots using common patterns
            roots = []
            
            # Languages to look for
            languages = {
                'Latin': ['Latin'],
                'Greek': ['Greek', 'Ancient Greek'],
                'French': ['French', 'Old French'],
                'Old English': ['Old English'],
                'Middle English': ['Middle English'], 
                'German': ['German', 'Old German', 'Middle High German'],
                'Spanish': ['Spanish'],
                'Italian': ['Italian'],
                'Proto-Germanic': ['Proto-Germanic', 'P.Gmc.'],
                'Proto-Indo-European': ['Proto-Indo-European', 'PIE', 'PIE root'],
                'Sanskrit': ['Sanskrit'],
                'Arabic': ['Arabic']
            }
            
            # Flatten the language map for regex pattern
            all_language_patterns = []
            for primary_lang, variants in languages.items():
                for variant in variants:
                    all_language_patterns.append(variant)
            
            # Map from variant to primary language
            variant_to_primary = {}
            for primary, variants in languages.items():
                for variant in variants:
                    variant_to_primary[variant] = primary
            
            # Different patterns to match etymology statements
            if etymology_text:
                etymology_patterns = [
                    rf'from\s+({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                    rf'({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                    rf'borrowed\s+from\s+({"|".join(all_language_patterns)})\s+["\']?(\w+)["\']?',
                    rf'from\s+({"|".join(all_language_patterns)})\s+(?:word|root|stem)\s+["\']?(\w+)["\']?'
                ]
                
                for pattern in etymology_patterns:
                    matches = re.findall(pattern, etymology_text)
                    for match in matches:
                        variant_lang, word_origin = match
                        
                        # Map the variant to primary language
                        primary_lang = variant_to_primary.get(variant_lang, variant_lang)
                        
                        if not any(r.get('word') == word_origin and r.get('language') == primary_lang for r in roots):
                            roots.append({
                                "word": word_origin,
                                "language": primary_lang,
                                "definition": f"Origin of {word}",
                                "year": None,
                                "roots": []
                            })
                            
                # Try more general patterns if specific ones didn't work
                if not roots:
                    general_patterns = [
                        r'from\s+([A-Z][a-z]+)\s+["\']?(\w+)["\']?',  # from X "Y"
                        r'cognate\s+with\s+([A-Z][a-z]+)\s+["\']?(\w+)["\']?',  # cognate with X "Y"
                    ]
                    
                    for pattern in general_patterns:
                        matches = re.findall(pattern, etymology_text)
                        for match in matches:
                            lang, word_origin = match
                            
                            # Skip common words mistaken for languages
                            skip_words = ['the', 'and', 'also', 'see', 'its', 'this', 'other', 'with', 'from']
                            if lang.lower() in skip_words or len(lang) < 3:
                                continue
                                
                            if not any(r.get('word') == word_origin and r.get('language') == lang for r in roots):
                                roots.append({
                                    "word": word_origin,
                                    "language": lang,
                                    "definition": f"Origin of {word}",
                                    "year": None,
                                    "roots": []
                                })
            
            return {
                "word": word,
                "language": language,
                "definition": definition,
                "year": None,  # This API typically doesn't provide year information
                "roots": roots
            }
            
        except Exception as e:
            logger.debug(f"FreeDictionary lookup failed for {word}: {str(e)}")
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

    def process_word(self, word, language="English"):
        """Process a single word and save its etymology data."""
        word = word.lower().strip()
        
        # Skip already processed words
        if word in getattr(self, 'processed_words', set()):
            self.logger.debug(f"Skipping already processed word: {word}")
            return True
        
        try:
            # Fetch etymology data
            etymology_data = self.fetch_etymology(word, language)
            
            if etymology_data:
                # Update statistics
                self.words_processed += 1
                self.successful_words += 1
                
                # Count connections
                if "roots" in etymology_data and etymology_data["roots"]:
                    self.connections_made += len(etymology_data["roots"])
                
                # Save data to disk if not in test mode
                if not self.test_mode:
                    output_file = self.output_dir / f"{language}_{word}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(etymology_data, f, indent=2, ensure_ascii=False)
                else:
                    # For testing, store in memory
                    self.results[f"{language}_{word}"] = etymology_data
                
                return True
            else:
                self.words_processed += 1
                self.failed_words += 1
                self.logger.warning(f"Failed to find etymology for {word}")
                return False
            
        except Exception as e:
            self.words_processed += 1
            self.failed_words += 1
            self.logger.error(f"Error processing {word}: {str(e)}")
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

    def estimate_dataset_size(self, word_lists):
        """Estimate dataset size and processing time."""
        # Calculate some statistics for logging
        total_words = sum(len(words) for words in word_lists.values())
        avg_roots_per_word = 3  # Estimated average
        total_connections = total_words * avg_roots_per_word
        total_size_mb = total_words * 0.015  # Estimated average file size in MB
        
        # Estimated processing time
        words_per_minute = 20  # Conservative estimate
        minutes_needed = total_words / words_per_minute
        days_needed = minutes_needed / (60 * 24)
        
        self.logger.info(f"Estimated dataset size: {total_size_mb:.2f} MB")
        self.logger.info(f"Estimated total words: {total_words}")
        self.logger.info(f"Estimated total connections: {total_connections}")
        self.logger.info(f"Estimated processing time: {days_needed:.2f} days")
        
        return {
            "total_words": total_words,
            "total_connections": total_connections,
            "total_size_mb": total_size_mb,
            "days_needed": days_needed
        }

    def run(self):
        """Run the etymology generator on the word lists."""
        start_time = time.time()
        
        try:
            # Get word lists for each language
            word_lists = self.fetch_word_lists()
            
            # Estimate dataset size
            dataset_info = self.estimate_dataset_size(word_lists)
            
            # Set up progress tracking
            total_words = sum(len(words) for words in word_lists.values())
            words_per_minute = 20  # Conservative estimate
            
            # Process each language's words
            for language, words in word_lists.items():
                self.logger.info(f"Processing {len(words)} {language} words")
                
                # Set up progress bar
                with tqdm(total=len(words), desc=f"Processing {language} words") as pbar:
                    for word in words:
                        # Process individual word
                        success = self.process_word(word, language)
                        
                        # Update progress
                        pbar.update(1)
                        
                        # Break if max words reached
                        if self.max_words and self.words_processed >= self.max_words:
                            self.logger.info(f"Reached maximum word limit ({self.max_words})")
                            break
            
            # Save final state
            if not self.test_mode:
                self.save_state()
            
            # Log completion statistics
            end_time = time.time()
            elapsed_minutes = (end_time - start_time) / 60
            self.logger.info(f"Completed in {elapsed_minutes:.2f} minutes")
            self.logger.info(f"Total words processed: {self.words_processed}")
            self.logger.info(f"Successful words: {self.successful_words}")
            self.logger.info(f"Failed words: {self.failed_words}")
            self.logger.info(f"Total connections: {self.connections_made}")
            
            # Return statistics
            return {
                "words_processed": self.words_processed,
                "successful_words": self.successful_words,
                "failed_words": self.failed_words,
                "connections": self.connections_made,
                "elapsed_minutes": elapsed_minutes
            }
            
        except Exception as e:
            self.logger.error(f"Error running etymology generator: {str(e)}")
            return None

    def load_supplementary_data(self):
        """Load supplementary etymology data from known sources, or create seed data if none exists."""
        try:
            # Define paths for supplementary data files
            data_dir = Path("data")
            english_file = data_dir / "english_etymologies.json"
            latin_file = data_dir / "latin_roots.json"
            greek_file = data_dir / "greek_roots.json"
            french_file = data_dir / "french_etymologies.json"
            
            data = {}
            
            # Load data from files if they exist
            if english_file.exists():
                with open(english_file, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
            if latin_file.exists():
                with open(latin_file, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
            if greek_file.exists():
                with open(greek_file, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
            if french_file.exists():
                with open(french_file, 'r', encoding='utf-8') as f:
                    data.update(json.load(f))
                
            # If no data files exist, create seed data for common etymologies
            if not data:
                # Create dictionary of common English etymologies
                english_data = {
                    "etymology": {
                        "language": "English",
                        "year": 1398,
                        "roots": [
                            {"word": "etymologia", "language": "Latin", "year": 1200},
                            {"word": "ἐτυμολογία", "language": "Ancient Greek", "year": -300}
                        ]
                    },
                    "philosophy": {
                        "language": "English",
                        "year": 1300, 
                        "roots": [
                            {"word": "philosophia", "language": "Latin", "year": 100},
                            {"word": "φιλοσοφία", "language": "Ancient Greek", "year": -400}
                        ]
                    },
                    "democracy": {
                        "language": "English",
                        "year": 1570,
                        "roots": [
                            {"word": "dēmocratia", "language": "Medieval Latin", "year": 900},
                            {"word": "δημοκρατία", "language": "Ancient Greek", "year": -500}
                        ]
                    },
                    "computer": {
                        "language": "English",
                        "year": 1640,
                        "roots": [
                            {"word": "computare", "language": "Latin", "year": 300}
                        ]
                    },
                    "biology": {
                        "language": "English",
                        "year": 1819,
                        "roots": [
                            {"word": "biologia", "language": "New Latin", "year": 1766},
                            {"word": "βίος", "language": "Ancient Greek", "year": -500, "definition": "life", "transliteration": "bíos"},
                            {"word": "λογία", "language": "Ancient Greek", "year": -500, "definition": "study of", "transliteration": "logía"}
                        ]
                    }
                }
                
                # Add French etymologies
                french_data = {
                    "château": {
                        "language": "French",
                        "year": 1100,
                        "roots": [
                            {"word": "castellum", "language": "Latin", "year": 100, "definition": "castle, fort"},
                            {"word": "chastel", "language": "Old French", "year": 900}
                        ]
                    },
                    "bonjour": {
                        "language": "French",
                        "year": 1400,
                        "roots": [
                            {"word": "bon", "language": "French", "year": 1100, "definition": "good"},
                            {"word": "jour", "language": "French", "year": 1100, "definition": "day"}
                        ]
                    },
                    "café": {
                        "language": "French",
                        "year": 1700,
                        "roots": [
                            {"word": "qahwa", "language": "Arabic", "year": 1500, "definition": "coffee"}
                        ]
                    },
                    "merci": {
                        "language": "French",
                        "year": 1300,
                        "roots": [
                            {"word": "mercedem", "language": "Latin", "year": 100, "definition": "reward, favor, grace"}
                        ]
                    },
                    "fromage": {
                        "language": "French",
                        "year": 1200,
                        "roots": [
                            {"word": "formaticum", "language": "Late Latin", "year": 800, "definition": "formed cheese"}
                        ]
                    }
                }
                
                # Add Latin etymologies
                latin_data = {
                    "veni": {
                        "language": "Latin",
                        "year": -100,
                        "roots": [
                            {"word": "*gʷem-", "language": "Proto-Indo-European", "year": -3000, "definition": "to come"}
                        ]
                    },
                    "vidi": {
                        "language": "Latin",
                        "year": -100,
                        "roots": [
                            {"word": "*weid-", "language": "Proto-Indo-European", "year": -3000, "definition": "to see"}
                        ]
                    },
                    "vici": {
                        "language": "Latin",
                        "year": -100,
                        "roots": [
                            {"word": "*weik-", "language": "Proto-Indo-European", "year": -3000, "definition": "to fight, conquer"}
                        ]
                    },
                    "aqua": {
                        "language": "Latin",
                        "year": -100,
                        "roots": [
                            {"word": "*akʷā-", "language": "Proto-Indo-European", "year": -3000, "definition": "water"}
                        ]
                    },
                    "terra": {
                        "language": "Latin",
                        "year": -100,
                        "roots": [
                            {"word": "*ters-", "language": "Proto-Indo-European", "year": -3000, "definition": "dry"}
                        ]
                    }
                }
                
                # Add Greek etymologies
                greek_data = {
                    "logos": {
                        "language": "Greek",
                        "year": -500,
                        "roots": [
                            {"word": "λόγος", "language": "Ancient Greek", "year": -800, "definition": "word, speech, reason"}
                        ]
                    },
                    "cosmos": {
                        "language": "Greek",
                        "year": -500,
                        "roots": [
                            {"word": "κόσμος", "language": "Ancient Greek", "year": -800, "definition": "order, arrangement, ornament"}
                        ]
                    },
                    "pathos": {
                        "language": "Greek",
                        "year": -500,
                        "roots": [
                            {"word": "πάθος", "language": "Ancient Greek", "year": -800, "definition": "suffering, emotion"}
                        ]
                    },
                    "ethos": {
                        "language": "Greek",
                        "year": -500,
                        "roots": [
                            {"word": "ἦθος", "language": "Ancient Greek", "year": -800, "definition": "character, custom"}
                        ]
                    },
                    "chronos": {
                        "language": "Greek",
                        "year": -500,
                        "roots": [
                            {"word": "χρόνος", "language": "Ancient Greek", "year": -800, "definition": "time"}
                        ]
                    }
                }
                
                # Combine all data
                data = {**english_data, **french_data, **latin_data, **greek_data}
                
                self.logger.info(f"Created supplementary data with {len(data)} essential entries")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading supplementary data: {e}")
            return {}

    def initialize_language_detection(self):
        """Initialize language detection modules and patterns."""
        # Standard language prefixes
        self.language_prefixes = {
            # English variants
            "Middle English": "English",
            "Old English": "English",
            "Early Modern English": "English",
            "Late Middle English": "English",
            "Early Middle English": "English",
            
            # Latin variants
            "Late Latin": "Latin",
            "Medieval Latin": "Latin",
            "New Latin": "Latin",
            "Vulgar Latin": "Latin",
            "Ecclesiastical Latin": "Latin",
            "Classical Latin": "Latin",
            
            # Greek variants
            "Koine Greek": "Greek",
            "Byzantine Greek": "Greek",
            "Mycenaean Greek": "Greek",
            "Ancient Greek": "Greek",
            "Modern Greek": "Greek",
            "Hellenistic Greek": "Greek",
            
            # French variants
            "Old French": "French",
            "Middle French": "French",
            "Norman French": "French",
            "Anglo-Norman": "French",
            "Anglo-French": "French",
            
            # German variants
            "Old High German": "German",
            "Middle High German": "German",
            "Early New High German": "German",
            
            # Norse/Scandinavian variants
            "Old Norse": "Norse",
            "Old Swedish": "Swedish",
            "Old Danish": "Danish",
            "Old Norwegian": "Norwegian",
            "Old Icelandic": "Icelandic",
            
            # Celtic variants
            "Old Irish": "Irish",
            "Middle Irish": "Irish",
            "Old Welsh": "Welsh",
            "Middle Welsh": "Welsh",
            "Gaulish": "Celtic",
            "Brythonic": "Celtic",
            "Proto-Celtic": "Celtic",
            
            # Spanish variants
            "Old Spanish": "Spanish",
            
            # Italian variants
            "Old Italian": "Italian",
            
            # Portuguese variants
            "Old Portuguese": "Portuguese",
            
            # Arabic variants
            "Classical Arabic": "Arabic",
            
            # Dutch variants
            "Middle Dutch": "Dutch",
            "Old Dutch": "Dutch",
            
            # Russian variants
            "Old Russian": "Russian",
            "Old East Slavic": "Russian",
            
            # Indo-European variants
            "Proto-Indo-European": "Indo-European",
            "Proto-Germanic": "Germanic",
            "Proto-Romance": "Romance",
            "Proto-Slavic": "Slavic",
            "Proto-Italic": "Italic",
            "Proto-Balto-Slavic": "Balto-Slavic",
            "Proto-Celtic": "Celtic",
            "Proto-Greek": "Greek"
        }

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