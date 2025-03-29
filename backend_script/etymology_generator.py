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
                 geo_data=False, geo_mapping=None, oed_api_key=None):
        """Initialize the etymology generator."""
        # Basic setup and logging configuration
        self.test_mode = test_mode
        self.logger = logging.getLogger("etymology_generator")
        self.sources = sources.split(',') if sources else ["wiktionary", "etymonline"]
        self.geo_data = geo_data
        self.geo_mapping_file = geo_mapping
        self.oed_api_key = oed_api_key
        
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
        """Load the configured etymology data sources."""
        self.data_sources = {}
        
        for source in self.sources:
            self.logger.info(f"Initializing data source: {source}")
            
            if source == "wiktionary":
                self.data_sources[source] = self.init_wiktionary_source()
            elif source == "etymonline":
                self.data_sources[source] = self.init_etymonline_source()
            elif source == "oed":
                if not self.oed_api_key:
                    self.logger.warning("OED API key not provided, skipping OED data source")
                    continue
                self.data_sources[source] = self.init_oed_source()
            elif source == "ielex":
                self.data_sources[source] = self.init_ielex_source()
            elif source == "starling":
                self.data_sources[source] = self.init_starling_source()
            elif source == "etymwordnet":
                self.data_sources[source] = self.init_etymwordnet_source()
            elif source == "pokorny":
                self.data_sources[source] = self.init_pokorny_source()
            elif source == "cooljugator":
                self.data_sources[source] = self.init_cooljugator_source()
            else:
                self.logger.warning(f"Unknown data source: {source}")
                
        self.logger.info(f"Initialized {len(self.data_sources)} data sources")

    def init_wiktionary_source(self):
        """Initialize the Wiktionary data source."""
        wiktionary_cache = self.cache_dir / "wiktionary"
        
        # Check if we have the latest Wiktionary data
        wiktionary_index = wiktionary_cache / "index.json"
        
        if not os.path.exists(wiktionary_index):
            self.logger.info("Downloading Wiktionary index...")
            # In a real implementation, we would download the actual Wiktionary dumps
            # For now, we'll just create a placeholder
            with open(wiktionary_index, 'w') as f:
                json.dump({"last_updated": time.time()}, f)
        
        return {"cache_dir": wiktionary_cache, "index": wiktionary_index}

    def init_etymonline_source(self):
        """Initialize the Etymonline data source."""
        etymonline_cache = self.cache_dir / "etymonline"
        return {"cache_dir": etymonline_cache}

    def init_oed_source(self):
        """Initialize the Oxford English Dictionary API source."""
        return {"api_key": self.oed_api_key, "base_url": "https://languages.oup.com/api/v1/oed/"}

    def init_ielex_source(self):
        """Initialize the University of Texas Indo-European Lexicon source."""
        ielex_cache = self.cache_dir / "ielex"
        ielex_data = ielex_cache / "ielex_data.json"
        
        if not os.path.exists(ielex_data):
            self.logger.info("Downloading Indo-European Lexicon data...")
            # In a real implementation, we would scrape or download the IELEX data
            # For now, we'll just create a placeholder
            with open(ielex_data, 'w') as f:
                json.dump({"last_updated": time.time()}, f)
                
        return {"cache_dir": ielex_cache, "data_file": ielex_data}
        
    def init_starling_source(self):
        """Initialize the Tower of Babel (Starling) database source."""
        starling_cache = self.cache_dir / "starling"
        return {"cache_dir": starling_cache}

    def init_etymwordnet_source(self):
        """Initialize the Etymological Wordnet source."""
        etymwordnet_cache = self.cache_dir / "etymwordnet"
        etymwordnet_data = etymwordnet_cache / "etymwn.tsv"
        
        if not os.path.exists(etymwordnet_data):
            self.logger.info("Downloading Etymological Wordnet data...")
            # In a real implementation, we would download the actual data
            # For demonstration, we'll create a small sample file
            with open(etymwordnet_data, 'w') as f:
                f.write("eng:muscle\trel:derived\tdeu:Maus\n")
                f.write("eng:etymology\trel:derived\tgrc:ἐτυμολογία\n")
                
        return {"cache_dir": etymwordnet_cache, "data_file": etymwordnet_data}

    def init_pokorny_source(self):
        """Initialize Pokorny's Indo-European Etymological Dictionary source."""
        pokorny_cache = self.cache_dir / "pokorny"
        return {"cache_dir": pokorny_cache}

    def init_cooljugator_source(self):
        """Initialize the CoolJugator/EtymoloGeek source."""
        cooljugator_cache = self.cache_dir / "cooljugator"
        return {"cache_dir": cooljugator_cache}

    def load_geo_mapping(self):
        """Load the geographical mapping data for historical languages."""
        if self.geo_mapping_file and os.path.exists(self.geo_mapping_file):
            with open(self.geo_mapping_file, 'r', encoding='utf-8') as f:
                self.geo_mapping = json.load(f)
        else:
            # Default mapping
            self.geo_mapping = {
                "Latin": {
                    "ancient": {
                        "center": {"lat": 41.9028, "lng": 12.4964},
                        "location": "Rome, Italy",
                        "time_periods": {
                            "-500-500": {"lat": 41.9028, "lng": 12.4964, "radius": 500},
                            "500-1500": {"lat": 45.4642, "lng": 9.1900, "radius": 300}
                        }
                    }
                },
                "Ancient Greek": {
                    "ancient": {
                        "center": {"lat": 37.9838, "lng": 23.7275},
                        "location": "Athens, Greece",
                        "time_periods": {
                            "-800-0": {"lat": 37.9838, "lng": 23.7275, "radius": 300}
                        }
                    }
                },
                "Old French": {
                    "ancient": {
                        "center": {"lat": 48.8566, "lng": 2.3522},
                        "location": "Paris, France",
                        "time_periods": {
                            "800-1400": {"lat": 48.8566, "lng": 2.3522, "radius": 200}
                        }
                    }
                },
                "Proto-Indo-European": {
                    "ancient": {
                        "center": {"lat": 52.0000, "lng": 45.0000},
                        "location": "Pontic-Caspian steppe",
                        "time_periods": {
                            "-4500--2500": {"lat": 52.0000, "lng": 45.0000, "radius": 1000}
                        }
                    }
                }
            }
            
            # Add more language mappings
            self._extend_geo_mapping()
            
    def _extend_geo_mapping(self):
        """Extend the geographical mapping with additional languages."""
        # Germanic languages
        self.geo_mapping.update({
            "Old English": {
                "ancient": {
                    "center": {"lat": 51.5074, "lng": -0.1278},
                    "location": "England",
                    "time_periods": {
                        "450-1066": {"lat": 51.5074, "lng": -0.1278, "radius": 200}
                    }
                }
            },
            "Old High German": {
                "ancient": {
                    "center": {"lat": 49.4521, "lng": 11.0767},
                    "location": "Nuremberg, Germany",
                    "time_periods": {
                        "750-1050": {"lat": 49.4521, "lng": 11.0767, "radius": 300}
                    }
                }
            },
            "Old Norse": {
                "ancient": {
                    "center": {"lat": 59.9139, "lng": 10.7522},
                    "location": "Oslo, Norway",
                    "time_periods": {
                        "700-1300": {"lat": 59.9139, "lng": 10.7522, "radius": 500}
                    }
                }
            }
        })
        
        # Slavic languages
        self.geo_mapping.update({
            "Proto-Slavic": {
                "ancient": {
                    "center": {"lat": 50.0755, "lng": 14.4378},
                    "location": "Central Europe",
                    "time_periods": {
                        "-500-700": {"lat": 50.0755, "lng": 14.4378, "radius": 500}
                    }
                }
            },
            "Old Church Slavonic": {
                "ancient": {
                    "center": {"lat": 42.6977, "lng": 23.3219},
                    "location": "Sofia, Bulgaria",
                    "time_periods": {
                        "850-1100": {"lat": 42.6977, "lng": 23.3219, "radius": 300}
                    }
                }
            }
        })
        
        # Celtic languages
        self.geo_mapping.update({
            "Proto-Celtic": {
                "ancient": {
                    "center": {"lat": 48.8566, "lng": 2.3522},
                    "location": "Central Europe",
                    "time_periods": {
                        "-1200--500": {"lat": 48.8566, "lng": 2.3522, "radius": 600}
                    }
                }
            },
            "Old Irish": {
                "ancient": {
                    "center": {"lat": 53.3498, "lng": -6.2603},
                    "location": "Dublin, Ireland",
                    "time_periods": {
                        "600-900": {"lat": 53.3498, "lng": -6.2603, "radius": 200}
                    }
                }
            }
        })
        
        # Add more as needed...

    def get_geo_data_for_word(self, word, language, year=None):
        """Get geographical data for a word based on its language and time period."""
        if not self.geo_data or language not in self.geo_mapping:
            return None
            
        geo_info = self.geo_mapping.get(language, {}).get("ancient", {})
        
        # Default to center coordinates
        result = {
            "lat": geo_info.get("center", {}).get("lat"),
            "lng": geo_info.get("center", {}).get("lng"),
            "location": geo_info.get("location", f"{language} region"),
            "confidence": 0.5  # Default medium confidence
        }
        
        # If we have a year, try to find a more specific location
        if year and "time_periods" in geo_info:
            try:
                # Convert year to int if it's a string
                if isinstance(year, str) and year.strip():
                    year = int(year)
                
                # Ensure year is an integer
                if isinstance(year, int):
                    for period, location in geo_info["time_periods"].items():
                        # Parse time period
                        try:
                            period_parts = period.split("-")
                            start = int(period_parts[0])
                            end = int(period_parts[1]) if len(period_parts) > 1 else start
                            
                            if start <= year <= end:
                                result["lat"] = location["lat"]
                                result["lng"] = location["lng"]
                                result["confidence"] = 0.8  # Higher confidence with time match
                                break
                        except (ValueError, IndexError):
                            continue
            except (ValueError, TypeError):
                # If year can't be parsed, just use default location
                pass
                    
        return result
        
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
                    
                    # Add geographical data if enabled
                    if self.geo_data:
                        # Add geo data for the main word
                        try:
                            geo_data = self.get_geo_data_for_word(word, language, result.get("year"))
                            if geo_data:
                                result["geo_origin"] = geo_data
                        except Exception as e:
                            self.logger.error(f"Error adding geo data for main word {word}: {str(e)}")
                            
                        # Add geo data for roots
                        for root in result["roots"]:
                            try:
                                root_lang = root.get("language")
                                root_year = root.get("year")
                                if root_lang:
                                    geo_data = self.get_geo_data_for_word(root.get("word"), root_lang, root_year)
                                    if geo_data:
                                        root["geo_origin"] = geo_data
                            except Exception as e:
                                self.logger.error(f"Error adding geo data for root {root.get('word', 'unknown')}: {str(e)}")
                    
                    # Log successful use of supplementary data
                    self.logger.debug(f"Added {len(result['roots'])} roots from supplementary data for {word}")
                    return result
            
            # Try each configured data source
            etymology_data = {}
            sources_used = []
            
            for source_name, source_config in self.data_sources.items():
                self.logger.debug(f"Trying source {source_name} for {word}")
                
                if source_name == "wiktionary":
                    source_data = self.fetch_from_wiktionary(word, language)
                elif source_name == "etymonline":
                    source_data = self.fetch_from_etymonline(word)
                elif source_name == "oed":
                    source_data = self.fetch_from_oed(word, language)
                elif source_name == "ielex":
                    source_data = self.fetch_from_ielex(word, language)
                elif source_name == "starling":
                    source_data = self.fetch_from_starling(word, language)
                elif source_name == "etymwordnet":
                    source_data = self.fetch_from_etymwordnet(word, language)
                elif source_name == "pokorny":
                    source_data = self.fetch_from_pokorny(word, language)
                elif source_name == "cooljugator":
                    source_data = self.fetch_from_cooljugator(word, language)
                else:
                    continue
                
                # Merge data from this source if it has useful information
                if source_data and (source_data.get("roots") or source_data.get("year")):
                    sources_used.append(source_name)
                    
                    # Merge definition
                    if not result["definition"] and source_data.get("definition"):
                        result["definition"] = source_data["definition"]
                    
                    # Use year if not set or if this source has a more precise year
                    if not result["year"] and source_data.get("year"):
                        result["year"] = source_data["year"]
                    
                    # Merge roots
                    if source_data.get("roots"):
                        # Add only new roots that aren't already in the result
                        existing_root_words = {r.get("word").lower() for r in result["roots"] if "word" in r}
                        for root in source_data["roots"]:
                            if root.get("word") and root.get("word").lower() not in existing_root_words:
                                result["roots"].append(root)
                                existing_root_words.add(root.get("word").lower())
            
            # Add sources used to the result
            if sources_used:
                result["sources"] = sources_used
            
            # Add geographical data if enabled and not already present
            if self.geo_data:
                # Add geo data for the main word
                try:
                    if not result.get("geo_origin"):
                        geo_data = self.get_geo_data_for_word(word, language, result.get("year"))
                        if geo_data:
                            result["geo_origin"] = geo_data
                except Exception as e:
                    self.logger.error(f"Error adding geo data for main word {word}: {str(e)}")
                
                # Add geo data for roots
                for root in result.get("roots", []):
                    try:
                        if not root.get("geo_origin"):
                            root_lang = root.get("language")
                            root_year = root.get("year")
                            if root_lang:
                                geo_data = self.get_geo_data_for_word(root.get("word"), root_lang, root_year)
                                if geo_data:
                                    root["geo_origin"] = geo_data
                    except Exception as e:
                        self.logger.error(f"Error adding geo data for root {root.get('word', 'unknown')}: {str(e)}")
                
            # Ensure we have etymology array for consistency
            if not result.get("etymology") and result.get("roots"):
                result["etymology"] = result["roots"]
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching etymology for {word}: {str(e)}")
            return result
            
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
            # Get the language code for the query
            lang_code = self.get_language_code(language)
            if not lang_code:
                self.logger.warning(f"Unknown language code for {language}")
                return result
                
            # Search for the word in the TSV file
            data_file = self.data_sources["etymwordnet"]["data_file"]
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        source_word = parts[0].split(':')
                        relation = parts[1].split(':')[1]
                        target_word = parts[2].split(':')
                        
                        # Check if this line relates to our word
                        if source_word[0] == lang_code and source_word[1] == word and relation == "derived":
                            # Found a root word
                            target_lang = self.get_language_name(target_word[0])
                            root = {
                                "word": target_word[1],
                                "language": target_lang,
                                "year": None  # EtymWordnet doesn't provide years
                            }
                            result["roots"].append(root)
            
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
            # This would be a real implementation querying the IELEX data
            # For now, return a simple placeholder for demonstration
            if word == "etymology" and language == "English":
                result["roots"] = [
                    {
                        "word": "*et-", 
                        "language": "Proto-Indo-European",
                        "definition": "true, real",
                        "year": -4500
                    }
                ]
                
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
        
        # This would be a real implementation querying the Starling database
        # For now, return an empty result
        return result

    def fetch_from_oed(self, word, language):
        """Fetch etymology data from the Oxford English Dictionary API."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        try:
            if language != "English":
                return result  # OED only covers English
                
            # This would be a real implementation using the OED API
            # For demonstration purposes, return some placeholder data
            if word == "computer":
                result["definition"] = "An electronic device for storing and processing data."
                result["year"] = 1640
                result["roots"] = [
                    {
                        "word": "compute",
                        "language": "English",
                        "year": 1631
                    },
                    {
                        "word": "computare",
                        "language": "Latin",
                        "definition": "to calculate, to count",
                        "year": 100
                    }
                ]
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching from OED for {word}: {str(e)}")
            return result

    def fetch_from_pokorny(self, word, language):
        """Fetch etymology data from Pokorny's Indo-European Etymological Dictionary."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        # This would be a real implementation parsing Pokorny's dictionary
        # For now, return an empty result
        return result

    def fetch_from_cooljugator(self, word, language):
        """Fetch etymology data from CoolJugator/EtymoloGeek."""
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        try:
            # This would be a real implementation querying the CoolJugator API
            # For now, we'll just return placeholder data for certain words
            if word == "democracy" and language == "English":
                result["definition"] = "A system of government by the whole population."
                result["year"] = 1570
                result["roots"] = [
                    {
                        "word": "demokratia",
                        "language": "Ancient Greek",
                        "definition": "popular government",
                        "year": -500
                    }
                ]
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching from CoolJugator for {word}: {str(e)}")
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