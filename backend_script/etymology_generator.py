#!/usr/bin/env python3
import os
import json
import time
import random
import logging
import argparse
import requests
import re
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import xml.etree.ElementTree as ET
import gzip
import urllib.request

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
    def __init__(self, max_words=None, languages=None, test_mode=False, sources=None, 
                 geo_data=False, geo_mapping=None):
        """Initialize the etymology generator."""
        # Basic setup and logging configuration
        self.test_mode = test_mode
        self.logger = logging.getLogger("etymology_generator")
        self.sources = sources.split(',') if sources else ["wiktionary", "etymonline", "etymwordnet", "ielex", "starling"]
        self.geo_data = geo_data
        self.geo_mapping_file = geo_mapping
        
        # Configure output files and directories
        self.output_dir = self.setup_output_directory()
        self.cache_dir = self.setup_cache_directory()
        
        # Initialize language detection and NLP tools
        self.initialize_language_detection()
        
        # Initialize geo data mapping if enabled
        if self.geo_data:
            self.load_geo_mapping()
        
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

        # Load additional data sources
        self.load_data_sources()
        
        self.logger.info(f"Starting etymology generator (test mode: {test_mode})")

    def setup_output_directory(self):
        """Set up the output directory for storing etymology data."""
        output_dir = Path("./output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
        
    def setup_cache_directory(self):
        """Set up the cache directory for storing downloaded data."""
        cache_dir = Path("./cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Create subdirectories for each data source
        for source in self.sources:
            source_dir = cache_dir / source
            if not os.path.exists(source_dir):
                os.makedirs(source_dir)
        
        return cache_dir

    def load_data_sources(self):
        """Load and initialize configured data sources."""
        available_sources = {
            "wiktionary": self.init_wiktionary_source,
            "etymonline": self.init_etymonline_source,
            "etymwordnet": self.init_etymwordnet_source,
            "ielex": self.init_ielex_source,
            "starling": self.init_starling_source
        }
        
        # Parse the source list
        source_list = [s.strip().lower() for s in self.sources]
        
        # Initialize the data_sources dictionary
        self.data_sources = {}
        
        # Initialize each requested source
        for source in source_list:
            if source in available_sources:
                self.logger.info(f"Initializing data source: {source}")
                try:
                    # Call the initialization function and store its return value
                    source_data = available_sources[source]()
                    # Store the source's data in the data_sources dict
                    self.data_sources[source] = source_data
                except Exception as e:
                    self.logger.error(f"Error initializing {source}: {str(e)}")
            else:
                self.logger.warning(f"Unknown data source: {source}")
                
        # Make sure the data directories exist
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Log the initialized sources
        self.logger.info(f"Initialized {len(self.data_sources)} data sources")

    def init_wiktionary_source(self):
        """Initialize the Wiktionary data source."""
        wiktionary_cache = self.cache_dir / "wiktionary"
        
        # Check if we have the latest Wiktionary data
        wiktionary_index = wiktionary_cache / "index.json"
        
        if not os.path.exists(wiktionary_index):
            self.logger.info("Creating Wiktionary cache index...")
            with open(wiktionary_index, 'w') as f:
                json.dump({"last_updated": time.time()}, f)
        
        return {"cache_dir": wiktionary_cache, "index": wiktionary_index}

    def init_etymonline_source(self):
        """Initialize the Etymonline data source."""
        etymonline_cache = self.cache_dir / "etymonline"
        return {"cache_dir": etymonline_cache}

    def init_ielex_source(self):
        """Initialize the University of Texas Indo-European Lexicon source."""
        ielex_cache = self.cache_dir / "ielex"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(ielex_cache):
            os.makedirs(ielex_cache)
            
        return {"cache_dir": ielex_cache, "base_url": "https://lrc.la.utexas.edu/lex/master"}
        
    def init_starling_source(self):
        """Initialize the Tower of Babel (Starling) database source."""
        starling_cache = self.cache_dir / "starling"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(starling_cache):
            os.makedirs(starling_cache)
            
        return {"cache_dir": starling_cache, "base_url": "https://starling.rinet.ru/cgi-bin/response.cgi"}

    def init_etymwordnet_source(self):
        """Initialize the etymological wordnet data source by downloading the dataset if needed."""
        etymwordnet_cache = self.cache_dir / "etymwordnet"
        data_file = etymwordnet_cache / "etymwn.tsv"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(etymwordnet_cache):
            os.makedirs(etymwordnet_cache)
        
        # Check if we need to download the data
        if not os.path.exists(data_file):
            self.logger.info("Downloading Etymological Wordnet dataset...")
            try:
                # Etymological Wordnet URL
                etymwn_url = "http://www1.icsi.berkeley.edu/~demelo/etymwn/etymwn.tsv"
                
                # Download the file
                response = requests.get(etymwn_url, stream=True)
                response.raise_for_status()  # Raise an error for bad responses
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                
                self.logger.info(f"Downloading {total_size/1024/1024:.1f} MB...")
                
                with open(data_file, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                
                self.logger.info("Download complete!")
            except Exception as e:
                self.logger.error(f"Failed to download Etymological Wordnet: {str(e)}")
                self.logger.info("Creating sample data instead...")
                
                # As a fallback, we'll create a sample data file
                data_file = etymwordnet_cache / "etymwn_sample.tsv"
                self.create_sample_etymwn_data(data_file)
        
        # Load the data into memory
        self.etymwordnet_data = self.load_etymwn_data(data_file)
        
        return {
            "cache_dir": etymwordnet_cache,
            "data_file": data_file
        }
    
    def create_sample_etymwn_data(self, sample_file):
        """Create a sample Etymological Wordnet data file if download fails."""
        self.logger.info("Creating sample Etymological Wordnet data")
        
        # Sample data with etymological relationships in TSV format
        sample_data = [
            # Format: lang:word <tab> rel <tab> lang:word
            "eng:etymology\trel:derived\tgrc:ἐτυμολογία",
            "eng:biology\trel:derived\tgrc:βιολογία",
            "eng:computer\trel:derived\tlat:computare",
            "eng:philosophy\trel:derived\tgrc:φιλοσοφία",
            "eng:democracy\trel:derived\tgrc:δημοκρατία",
            "fra:bonjour\trel:derived\tlat:bonus diurnus",
            "fra:merci\trel:derived\tlat:merces",
            "fra:château\trel:derived\tlat:castellum",
            "fra:fromage\trel:derived\tlat:formaticum",
            "fra:café\trel:derived\tara:قهوة",
            "lat:veni\trel:derived\tine:*gʷem-",
            "lat:vidi\trel:derived\tine:*weid-",
            "lat:vici\trel:derived\tine:*weik-",
            "lat:aqua\trel:derived\tine:*akʷā-",
            "lat:terra\trel:derived\tine:*ters-",
            "grc:logos\trel:derived\tine:*leg-",
            "grc:cosmos\trel:derived\tine:*kens-",
            "grc:pathos\trel:derived\tine:*kwent-",
            "grc:ethos\trel:derived\tine:*swedh-",
            "grc:chronos\trel:derived\tine:*gher-"
        ]

        # Write sample data to TSV
        with open(sample_file, 'w', encoding='utf-8') as f:
            for line in sample_data:
                f.write(f"{line}\n")
                
        self.logger.info(f"Created sample data with {len(sample_data)} entries")
    
    def load_etymwn_data(self, data_file):
        """Load Etymological Wordnet data from file into memory."""
        self.logger.info(f"Loading Etymological Wordnet data from {data_file}")
        
        # Dictionary to store etymological relationships
        etymwn_data = {}
        
        # Record count for logging
        count = 0
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    count += 1
                    if count % 100000 == 0:
                        self.logger.info(f"Processed {count} lines from etymwn")
                    
                    # Parse the line: source \t relation \t target
                    parts = line.strip().split('\t')
                    if len(parts) != 3:
                        continue
                    
                    source, relation, target = parts
                    
                    # Only consider etymological derivation relationships
                    if not relation.startswith('rel:derives') and not relation.startswith('rel:derived'):
                        continue
                    
                    # Parse the source and target: lang:word
                    try:
                        source_lang, source_word = source.split(':', 1)
                        target_lang, target_word = target.split(':', 1)
                    except ValueError:
                        continue
                    
                    # Store the relationship
                    if source_lang not in etymwn_data:
                        etymwn_data[source_lang] = {}
                    
                    if source_word not in etymwn_data[source_lang]:
                        etymwn_data[source_lang][source_word] = {
                            "derived_from": [],
                            "derived_to": []
                        }
                    
                    # Store the relationship based on direction
                    if relation.startswith('rel:derives'):
                        # target is derived from source
                        if {"lang": target_lang, "word": target_word} not in etymwn_data[source_lang][source_word]["derived_to"]:
                            etymwn_data[source_lang][source_word]["derived_to"].append({"lang": target_lang, "word": target_word})
                    else:
                        # source is derived from target
                        if {"lang": target_lang, "word": target_word} not in etymwn_data[source_lang][source_word]["derived_from"]:
                            etymwn_data[source_lang][source_word]["derived_from"].append({"lang": target_lang, "word": target_word})
                    
                    # Also create an entry for the target if it doesn't exist
                    if target_lang not in etymwn_data:
                        etymwn_data[target_lang] = {}
                    
                    if target_word not in etymwn_data[target_lang]:
                        etymwn_data[target_lang][target_word] = {
                            "derived_from": [],
                            "derived_to": []
                        }
                    
                    # Add the reverse relationship
                    if relation.startswith('rel:derives'):
                        # target is derived from source
                        if {"lang": source_lang, "word": source_word} not in etymwn_data[target_lang][target_word]["derived_from"]:
                            etymwn_data[target_lang][target_word]["derived_from"].append({"lang": source_lang, "word": source_word})
                    else:
                        # source is derived from target
                        if {"lang": source_lang, "word": source_word} not in etymwn_data[target_lang][target_word]["derived_to"]:
                            etymwn_data[target_lang][target_word]["derived_to"].append({"lang": source_lang, "word": source_word})
            
            self.logger.info(f"Loaded {count} relationships from Etymological Wordnet")
            self.logger.info(f"Created {sum(len(words) for words in etymwn_data.values())} word entries")
            
            return etymwn_data
            
        except Exception as e:
            self.logger.error(f"Error loading etymwn data: {str(e)}")
            return {}

    def fetch_from_etymwordnet(self, word, language):
        """Fetch etymology data from Etymological Wordnet."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        try:
            # Check if etymwordnet is in our data sources
            if "etymwordnet" not in self.data_sources:
                self.logger.warning("Etymwordnet source not initialized")
                return result
                
            # Get the language code for the query
            lang_code = self.get_language_code(language)
            if not lang_code:
                self.logger.warning(f"Unknown language code for {language}")
                return result
                
            # Check the in-memory etymwn data
            self.logger.info(f"Checking etymwordnet for {word} ({lang_code})")
            
            word_lower = word.lower()
            
            if hasattr(self, 'etymwordnet_data') and lang_code in self.etymwordnet_data and word_lower in self.etymwordnet_data[lang_code]:
                word_data = self.etymwordnet_data[lang_code][word_lower]
                self.logger.info(f"Found {word} in etymwordnet data")
                
                # Process derived_from relationships to find roots
                for root_entry in word_data.get("derived_from", []):
                    root_lang_code = root_entry["lang"]
                    root_word = root_entry["word"]
                    
                    target_lang = self.get_language_name(root_lang_code)
                    
                    # Create the root entry
                    root = {
                        "word": root_word,
                        "language": target_lang,
                        "year": None,
                        "definition": ""
                    }
                    
                    # Estimate year based on language
                    if target_lang == "Latin":
                        root["year"] = -100  # Classical Latin period
                    elif target_lang == "Ancient Greek":
                        root["year"] = -400  # Classical Greek period
                    elif target_lang == "Proto-Indo-European":
                        root["year"] = -4500  # Estimated PIE period
                    elif target_lang == "Old French":
                        root["year"] = 1000  # Old French period
                    elif target_lang == "Arabic":
                        root["year"] = 700  # Classical Arabic period
                        
                    # Add the root if not already present
                    if not any(r.get("word") == root_word and r.get("language") == target_lang for r in result["roots"]):
                        result["roots"].append(root)
                        self.logger.info(f"Added root: {root_word} ({target_lang})")
            
            # If we found roots, return the result
            if result["roots"]:
                return result
            
            # If no roots found in etymwn data, fall back to our known pairs table
            known_pairs = {
                "English": {
                    "etymology": {"word": "ἐτυμολογία", "language": "Ancient Greek", "year": -400, "definition": "The study of the origin of words"},
                    "biology": {"word": "βιολογία", "language": "Ancient Greek", "year": -400, "definition": "The study of life"},
                    "philosophy": {"word": "φιλοσοφία", "language": "Ancient Greek", "year": -400, "definition": "Love of wisdom"},
                    "democracy": {"word": "δημοκρατία", "language": "Ancient Greek", "year": -400, "definition": "Rule by the people"}
                },
                "French": {
                    "bonjour": {"word": "bonus diurnus", "language": "Latin", "year": -100, "definition": "Good day"},
                    "merci": {"word": "merces", "language": "Latin", "year": -100, "definition": "Reward, payment"},
                    "château": {"word": "castellum", "language": "Latin", "year": -100, "definition": "Castle, fort"}
                },
                "Latin": {
                    "veni": {"word": "*gʷem-", "language": "Proto-Indo-European", "year": -4500, "definition": "To come"},
                    "vidi": {"word": "*weid-", "language": "Proto-Indo-European", "year": -4500, "definition": "To see"}
                },
                "Greek": {
                    "logos": {"word": "*leg-", "language": "Proto-Indo-European", "year": -4500, "definition": "To collect, speak"},
                    "cosmos": {"word": "*kens-", "language": "Proto-Indo-European", "year": -4500, "definition": "To announce, proclaim"}
                }
            }
            
            if language in known_pairs and word.lower() in known_pairs[language]:
                known_root = known_pairs[language][word.lower()]
                root = {
                    "word": known_root["word"],
                    "language": known_root["language"],
                    "year": known_root.get("year"),
                    "definition": known_root.get("definition", "")
                }
                result["roots"].append(root)
                self.logger.info(f"Added known root: {root['word']} ({root['language']})")
                
                # For these known pairs, also set reasonable year and definition for the word itself if not already set
                if not result.get("year"):
                    if language == "English":
                        result["year"] = 1500  # Approximate for English words
                    elif language == "French":
                        result["year"] = 1200  # Approximate for French words
                    elif language == "Latin":
                        result["year"] = -100  # Classical Latin period
                    elif language == "Greek":
                        result["year"] = -500  # Classical Greek period
                
                if not result.get("definition") and known_root.get("definition"):
                    result["definition"] = f"Related to {known_root['definition']}"
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error fetching from EtymWordnet for {word}: {str(e)}")
            return result

    def fetch_from_ielex(self, word, language):
        """Fetch etymology data from the University of Texas Indo-European Lexicon."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        try:
            # Check cache first
            cache_file = self.data_sources["ielex"]["cache_dir"] / f"{language}_{word}.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    return cached_data
            
            # Get base URL from data sources
            if "ielex" not in self.data_sources or "base_url" not in self.data_sources["ielex"]:
                self.logger.warning("IELEX source not properly initialized")
                return result
                
            base_url = self.data_sources["ielex"]["base_url"]
            
            # Set up headers for requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # First, we need to find potential PIE roots that might relate to this word
            # We'll search the master index page
            master_url = f"{base_url}/index.html"
            
            self.logger.info(f"Searching IELEX for {word}")
            
            # Fetch the master index page
            try:
                response = requests.get(master_url, headers=headers, timeout=10)
                response.raise_for_status()
            except Exception as e:
                self.logger.error(f"Failed to fetch IELEX master index: {str(e)}")
                return result
                
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all links to root pages
            root_links = soup.find_all('a')
            potential_roots = []
            
            # Get language code for search
            lang_code = self.get_language_code(language)
            search_word = word.lower()
            
            # Look through the roots to find potential matches
            for link in root_links:
                href = link.get('href')
                if not href or not href.endswith('.html'):
                    continue
                    
                # Extract the root from the href
                root_match = re.search(r'/([^/]+)\.html$', href)
                if not root_match:
                    continue
                    
                root_id = root_match.group(1)
                
                # If the link text contains our word or vice versa, add it to potential roots
                link_text = link.text.lower()
                if search_word in link_text or any(part in link_text for part in search_word.split()):
                    potential_roots.append((root_id, href))
                    self.logger.info(f"Found potential root: {root_id}")
            
            # If we don't find any direct matches, try looking for cognates
            if not potential_roots:
                # Find the most relevant page by checking for cognates
                all_lang_roots = []
                for link in root_links:
                    href = link.get('href')
                    if href and href.endswith('.html') and not href.startswith('http'):
                        # Only consider pages in the master directory
                        root_match = re.search(r'/([^/]+)\.html$', href)
                        if root_match:
                            all_lang_roots.append((root_match.group(1), href))
                
                # For each root page, check if it contains our language and word
                for root_id, href in all_lang_roots:
                    # Construct full URL if necessary
                    if href.startswith('/'):
                        root_url = f"https://lrc.la.utexas.edu{href}"
                    elif href.startswith('http'):
                        root_url = href
                    else:
                        root_url = f"{base_url}/{href}"
                        
                    try:
                        # Fetch the root page
                        root_response = requests.get(root_url, headers=headers, timeout=10)
                        root_response.raise_for_status()
                        
                        # Check if the page contains our word
                        if search_word in root_response.text.lower():
                            # Parse the page
                            root_soup = BeautifulSoup(root_response.text, 'html.parser')
                            
                            # Check for the language section
                            lang_sections = root_soup.find_all(['h2', 'h3', 'h4', 'b', 'strong'])
                            for section in lang_sections:
                                section_text = section.text.lower()
                                if language.lower() in section_text or (lang_code and lang_code.lower() in section_text):
                                    # Found the language section, now check for the word
                                    next_elem = section.next_sibling
                                    while next_elem and not (hasattr(next_elem, 'name') and next_elem.name in ['h2', 'h3', 'h4']):
                                        if hasattr(next_elem, 'text') and search_word in next_elem.text.lower():
                                            potential_roots.append((root_id, href))
                                            self.logger.info(f"Found cognate in root: {root_id}")
                                            break
                                        next_elem = next_elem.next_sibling
                    except Exception as e:
                        self.logger.warning(f"Error checking root page {root_id}: {str(e)}")
                        continue
            
            # Process the potential roots
            for root_id, href in potential_roots:
                # Construct full URL if necessary
                if href.startswith('/'):
                    root_url = f"https://lrc.la.utexas.edu{href}"
                elif href.startswith('http'):
                    root_url = href
                else:
                    root_url = f"{base_url}/{href}"
                
                try:
                    # Fetch the root page
                    root_response = requests.get(root_url, headers=headers, timeout=10)
                    root_response.raise_for_status()
                    
                    # Parse the page
                    root_soup = BeautifulSoup(root_response.text, 'html.parser')
                    
                    # Extract the PIE root
                    pie_root = ""
                    title = root_soup.find('title')
                    if title:
                        title_text = title.text
                        pie_match = re.search(r'Indo-European\s+Roots?\s+\*([^\s*]+)', title_text)
                        if pie_match:
                            pie_root = "*" + pie_match.group(1)
                            
                    if not pie_root:
                        # Try to find the root in the page content
                        for tag in root_soup.find_all(['h1', 'h2', 'h3']):
                            if 'Root' in tag.text:
                                root_text = tag.text
                                pie_match = re.search(r'\*([^\s*]+)', root_text)
                                if pie_match:
                                    pie_root = "*" + pie_match.group(1)
                                    break
                    
                    # If we still don't have a root, use the root ID
                    if not pie_root:
                        pie_root = "*" + root_id
                    
                    # Extract definition
                    definition = ""
                    definition_elem = root_soup.find('p')
                    if definition_elem:
                        definition = definition_elem.text.strip()
                        # Clean up the definition
                        definition = re.sub(r'\s+', ' ', definition)
                        definition = re.sub(r'^\*[^\s]+\s+', '', definition)
                    
                    # Create the root object
                    pie_root_obj = {
                        "word": pie_root,
                        "language": "Proto-Indo-European",
                        "year": -4500,  # Estimated PIE period
                        "definition": definition
                    }
                    
                    # Add the root if not already present
                    if not any(r.get("word") == pie_root_obj["word"] for r in result["roots"]):
                        result["roots"].append(pie_root_obj)
                        self.logger.info(f"Added PIE root: {pie_root}")
                        
                except Exception as e:
                    self.logger.warning(f"Error processing root {root_id}: {str(e)}")
                    continue
            
            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching from IELEX for {word}: {str(e)}")
            return result

    def fetch_from_starling(self, word, language):
        """Fetch etymology data from the Tower of Babel (Starling) database."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        try:
            # Check cache first
            cache_file = self.data_sources["starling"]["cache_dir"] / f"{language}_{word}.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    return cached_data
            
            # Get base URL from data sources
            if "starling" not in self.data_sources or "base_url" not in self.data_sources["starling"]:
                self.logger.warning("Starling source not properly initialized")
                return result
                
            base_url = self.data_sources["starling"]["base_url"]
            
            # Set up headers for requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Map language to Starling database
            db_mappings = {
                "English": "germanic",
                "German": "germanic",
                "Dutch": "germanic",
                "Swedish": "germanic",
                "Russian": "slavonic",
                "Polish": "slavonic",
                "Czech": "slavonic",
                "Bulgarian": "slavonic",
                "Latin": "romance",
                "French": "romance",
                "Italian": "romance",
                "Spanish": "romance",
                "Portuguese": "romance",
                "Ancient Greek": "greek",
                "Greek": "greek"
            }
            
            # Determine which database to search
            db_name = db_mappings.get(language, None)
            if not db_name:
                self.logger.warning(f"Language {language} not supported in Starling database")
                return result
            
            self.logger.info(f"Searching Starling database '{db_name}' for {word}")
            
            # Construct the search URL
            params = {
                "root": "config",
                "an": "search",
                "dict": db_name,
                "text": word,
                "method": "substring"
            }
            
            search_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Fetch the search results
            try:
                response = requests.get(search_url, headers=headers, timeout=15)
                response.raise_for_status()
            except Exception as e:
                self.logger.error(f"Failed to search Starling database for {word}: {str(e)}")
                return result
                
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results - look for links to individual entries
            result_links = soup.find_all('a', href=lambda href: href and 'dbid' in href and 'single' in href)
            
            for link in result_links:
                href = link.get('href')
                # Extract the entry ID
                entry_id_match = re.search(r'dbid=(\d+)', href)
                if entry_id_match:
                    entry_id = entry_id_match.group(1)
                    
                    # Get the entry page
                    entry_url = f"{base_url}?single=1&dict={db_name}&dbid={entry_id}"
                    
                    try:
                        entry_response = requests.get(entry_url, headers=headers, timeout=15)
                        entry_response.raise_for_status()
                        
                        entry_soup = BeautifulSoup(entry_response.text, 'html.parser')
                        
                        # Look for the word/meaning and proto-form
                        word_found = False
                        proto_form = None
                        meaning = None
                        
                        # Find the table with the entry data
                        tables = entry_soup.find_all('table')
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows:
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    # Check if this is the word/meaning cell
                                    if any(label in cells[0].text.lower() for label in ["word", "meaning", "translation"]):
                                        if word.lower() in cells[1].text.lower():
                                            word_found = True
                                            meaning = cells[1].text.strip()
                                    
                                    # Look for proto-form
                                    if any(label in cells[0].text.lower() for label in ["proto", "reconstruction", "etymology"]):
                                        proto_text = cells[1].text.strip()
                                        # Extract a proto-form - typically starts with asterisk
                                        proto_match = re.search(r'\*([^\s,;]+)', proto_text)
                                        if proto_match:
                                            proto_form = f"*{proto_match.group(1)}"
                        
                        # If we found a match
                        if word_found and proto_form:
                            # Determine the proto-language
                            if db_name == "germanic":
                                proto_lang = "Proto-Germanic"
                            elif db_name == "slavonic":
                                proto_lang = "Proto-Slavic"
                            elif db_name == "romance":
                                proto_lang = "Proto-Indo-European"
                            elif db_name == "greek":
                                proto_lang = "Proto-Greek"
                            else:
                                proto_lang = "Proto-Indo-European"
                            
                            # Create the root entry
                            root = {
                                "word": proto_form,
                                "language": proto_lang,
                                "year": None,
                                "definition": meaning or ""
                            }
                            
                            # Set year based on language
                            if proto_lang == "Proto-Germanic":
                                root["year"] = -500
                            elif proto_lang == "Proto-Slavic":
                                root["year"] = 0
                            elif proto_lang == "Proto-Indo-European":
                                root["year"] = -4500
                            elif proto_lang == "Proto-Greek":
                                root["year"] = -1500
                            
                            # Add to roots if not already present
                            if not any(r.get("word") == proto_form for r in result["roots"]):
                                result["roots"].append(root)
                                self.logger.info(f"Added proto-form: {proto_form} ({proto_lang})")
                        
                    except Exception as e:
                        self.logger.warning(f"Error fetching entry {entry_id}: {str(e)}")
                        continue
            
            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching from Starling for {word}: {str(e)}")
            return result

    def get_language_code(self, language):
        """Convert language name to code used in external resources."""
        language_codes = {
            "English": "eng",
            "French": "fra",
            "German": "deu",
            "Latin": "lat",
            "Ancient Greek": "grc",
            "Greek": "ell",
            "Spanish": "spa",
            "Italian": "ita",
            "Portuguese": "por",
            "Russian": "rus"
            # Add more as needed
        }
        return language_codes.get(language)
        
    def get_language_name(self, code):
        """Convert language code to name."""
        language_names = {
            "eng": "English",
            "fra": "French",
            "deu": "German",
            "lat": "Latin",
            "grc": "Ancient Greek",
            "ell": "Greek",
            "spa": "Spanish",
            "ita": "Italian",
            "por": "Portuguese",
            "rus": "Russian"
            # Add more as needed
        }
        return language_names.get(code, code)

    def fetch_etymology(self, word, language):
        """Fetch etymology data from all configured sources."""
        # Initialize the result structure
        result = {
        "word": word,
        "language": language,
        "year": None,
        "definition": "",
        "roots": []
        }
        
        # Check the data directory first
        data_dir = Path("data/words")
        word_dir = data_dir / language.lower() / word[0].lower()
        word_file = word_dir / f"{word.lower()}.json"
        
        # If data already exists and we're in a recovery situation, load it
        if word_file.exists():
        try:
            with open(word_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                self.logger.info(f"Found existing data for {word}")
                return existing_data
        except Exception as e:
            self.logger.warning(f"Error loading existing data for {word}: {str(e)}")
        
        # Check our supplementary data for known etymologies
        if word.lower() in self.supplementary_data:
            self.logger.info(f"Found {word} in supplementary data")
            return self.supplementary_data[word.lower()]
        
        # Fetch from each configured source
        for source in self.sources:
            try:
                source_data = None
                
                if source == "wiktionary":
                    source_data = self.fetch_from_wiktionary(word, language)
                elif source == "etymonline":
                    source_data = self.fetch_from_etymonline(word, language)
                elif source == "etymwordnet":
                    source_data = self.fetch_from_etymwordnet(word, language)
                elif source == "ielex":
                    source_data = self.fetch_from_ielex(word, language)
                elif source == "starling":
                    source_data = self.fetch_from_starling(word, language)
                
                if source_data and source_data.get("roots"):
                    # Merge data, avoiding duplicates
                    self.merge_etymology_data(result, source_data)
                    self.logger.info(f"Added data from {source} for {word}")
            except Exception as e:
                self.logger.error(f"Error fetching from {source} for {word}: {str(e)}")
        
        # Ensure the word and language are set correctly
        result["word"] = word
        result["language"] = language
        
        # Save data to file for recovery
        self.save_etymology_data(result)
        
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
    
    def save_etymology_data(self, data):
        """Save etymology data to a file for future use and recovery."""
        if not data or not data.get("word") or not data.get("language"):
            return
            
        # Create directory structure if needed
        word = data["word"].lower()
        language = data["language"]
        
        data_dir = Path("data/words")
        lang_dir = data_dir / language.lower()
        first_letter_dir = lang_dir / word[0].lower()
        
        os.makedirs(first_letter_dir, exist_ok=True)
        
        # Save the file
        word_file = first_letter_dir / f"{word}.json"
        with open(word_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        self.logger.debug(f"Saved etymology data for {word} ({language})")

    def process_word(self, word, language="English"):
        """Process a word and store its etymology data."""
        self.logger.info(f"Processing test word: {word} ({language})")
        
        # Fetch etymology data
        etymology_data = self.fetch_etymology(word, language)
        
        if etymology_data:
            # Calculate the quality score for the etymology data
            quality_score = self.evaluate_data_quality(etymology_data)
            etymology_data["quality_score"] = quality_score
            
            # Store the result
            key = f"{language}_{word}"
            self.results[key] = etymology_data
            
            # Save to output file if not in test mode
            if not self.test_mode:
                output_file = self.output_dir / f"{language}_{word}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(etymology_data, f, indent=2)
            else:
                # In test mode, save to test output directory if it exists
                output_file = self.output_dir / f"{language}_{word}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(etymology_data, f, indent=2)
                self.logger.info(f"Saved test output to {output_file}")
            
            # Track progress
            self.words_processed += 1
            self.successful_words += 1
            self.connections_made += len(etymology_data.get("roots", []))
            
            # Display etymology summary
            self.logger.info(f"Etymology Summary for {word} ({language}), year: {etymology_data.get('year')}")
            self.logger.info(f"Definition: {etymology_data.get('definition', '')[:50]}...")
            
            roots = etymology_data.get("roots", [])
            if roots:
                self.logger.info(f"Root words ({len(roots)}):")
                for i, root in enumerate(roots, 1):
                    self.logger.info(f"  {i}. {root.get('word', '')} ({root.get('language', '')}), year: {root.get('year')}")
            else:
                self.logger.info("No root words found")
                
            self.logger.info(f"Successfully processed {word} with {len(roots)} connections")
            
            return etymology_data
        else:
            self.words_processed += 1
            self.failed_words += 1
            self.logger.warning(f"Failed to process {word}")
            return None
            
    def evaluate_data_quality(self, etymology_data):
        """Evaluate the quality of etymology data and return a score out of 100."""
        # Initialize score
        score = 0
        max_score = 100
        
        # 1. Has roots (25 points)
        if 'roots' in etymology_data and etymology_data['roots']:
            score += 25
            
            # Bonus points for multiple roots (up to 10)
            num_roots = len(etymology_data['roots'])
            if num_roots > 1:
                score += min(10, num_roots * 5)
        
        # 2. Has year (20 points)
        if 'year' in etymology_data and etymology_data['year']:
            score += 20
        
        # 3. Has definition (20 points)
        if 'definition' in etymology_data and etymology_data['definition'] and len(etymology_data['definition']) > 10:
            score += 20
            
        # 4. Has geographical data (15 points)
        if self.geo_data:
            if 'geo_origin' in etymology_data:
                score += 10
                
            # Check roots for geographical data
            if 'roots' in etymology_data:
                geo_roots = 0
                for root in etymology_data['roots']:
                    if 'geo_origin' in root:
                        geo_roots += 1
                
                # Award points based on percentage of roots with geo data
                if etymology_data['roots']:
                    geo_pct = geo_roots / len(etymology_data['roots'])
                    score += int(5 * geo_pct)
                    
        # 5. Check consistency (10 points)
        consistent = True
        
        # Language consistency
        if 'roots' in etymology_data and etymology_data['roots']:
            expected_language_progression = {
                "English": ["French", "Latin", "Greek", "Proto-Germanic", "Proto-Indo-European"],
                "French": ["Latin", "Greek", "Proto-Indo-European"],
                "German": ["Proto-Germanic", "Proto-Indo-European"],
                "Spanish": ["Latin", "Arabic", "Proto-Indo-European"],
                "Italian": ["Latin", "Proto-Indo-European"],
                "Latin": ["Proto-Indo-European"],
                "Greek": ["Proto-Indo-European"]
            }
            
            language = etymology_data.get('language')
            if language in expected_language_progression:
                expected = expected_language_progression[language]
                
                # Check if root languages are reasonable for this language
                for root in etymology_data['roots']:
                    root_lang = root.get('language')
                    if root_lang and not any(exp in root_lang for exp in expected):
                        consistent = False
                        break
        
        if consistent:
            score += 10
            
        # Ensure score doesn't exceed max
        return min(score, max_score)

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
                        "year": -150,
                        "roots": [
                            {"word": "*akʷā-", "language": "Proto-Indo-European", "year": -3000, "definition": "water"}
                        ]
                    },
                    "terra": {
                        "language": "Latin",
                        "year": -150,
                        "roots": [
                            {"word": "*ters-", "language": "Proto-Indo-European", "year": -3000, "definition": "dry"}
                        ]
                    }
                }
                
                # Add Greek etymologies
                greek_data = {
                    "logos": {
                        "language": "Greek",
                        "year": -800,
                        "roots": [
                            {"word": "λόγος", "language": "Ancient Greek", "year": -800, "definition": "word, speech, reason"}
                        ]
                    },
                    "cosmos": {
                        "language": "Greek",
                        "year": -700,
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
                        "year": -600,
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
        """Initialize language detection tools."""
        # Language mapping (ISO code to name)
        self.lang_codes = {
            "English": "en",
            "French": "fr",
            "German": "de",
            "Spanish": "es",
            "Italian": "it",
            "Portuguese": "pt",
            "Latin": "la",
            "Greek": "el",
            "Russian": "ru",
            "Arabic": "ar",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko"
        }
        
        # Initialize other NLP tools here if needed
        self.logger.debug("Initialized language detection tools")

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