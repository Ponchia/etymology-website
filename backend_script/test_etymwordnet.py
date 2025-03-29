#!/usr/bin/env python3
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_etymwordnet")

class EtymWordnetTest:
    def __init__(self):
        self.test_words = {
            "English": ["etymology", "computer", "biology", "philosophy"],
            "French": ["bonjour", "merci", "château", "café"],
            "Latin": ["veni", "vidi", "vici", "aqua"]
        }
        self.cache_dir = os.path.join(".", "cache")
        
        # Ensure cache directories exist
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "etymwordnet"), exist_ok=True)
        
        # Set up etymwordnet sample data
        self.setup_etymwordnet_sample()
        
    def setup_etymwordnet_sample(self):
        """Set up sample data for etymwordnet"""
        data_dir = os.path.join(".", "data")
        os.makedirs(data_dir, exist_ok=True)
        
        sample_file = os.path.join(data_dir, "etymwn_sample.csv")
        
        # Create sample data if file doesn't exist
        if not os.path.exists(sample_file):
            logger.info("Creating sample Etymological Wordnet data file")
            
            # Sample data with etymological relationships
            sample_data = {
                "eng": {
                    "etymology": {
                        "roots": ["grc:ἐτυμολογία"],
                        "year": 1398,
                        "definition": "The study of the origin and historical development of words"
                    },
                    "biology": {
                        "roots": ["grc:βιολογία"],
                        "year": 1819,
                        "definition": "The science of life and living organisms"
                    },
                    "computer": {
                        "roots": ["lat:computare"],
                        "year": 1646,
                        "definition": "An electronic device for storing and processing data"
                    }
                },
                "fra": {
                    "bonjour": {
                        "roots": ["lat:bonus diurnus"],
                        "year": 1100,
                        "definition": "Good day, a common greeting in French"
                    },
                    "merci": {
                        "roots": ["lat:merces"],
                        "year": 1200,
                        "definition": "Thank you, an expression of gratitude"
                    }
                },
                "lat": {
                    "veni": {
                        "roots": ["ine:*gʷem-"],
                        "year": -100,
                        "definition": "I came, first person singular perfect tense of venire"
                    },
                    "vidi": {
                        "roots": ["ine:*weid-"],
                        "year": -100,
                        "definition": "I saw, first person singular perfect tense of videre"
                    }
                }
            }
            
            # Write sample data to CSV
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("lang,word,roots,year,definition\n")
                for lang, words in sample_data.items():
                    for word, data in words.items():
                        roots = "|".join(data["roots"])
                        year = data.get("year", "")
                        definition = data.get("definition", "").replace(",", ";")
                        f.write(f"{lang},{word},{roots},{year},{definition}\n")
                        
        # Load sample data into memory
        self.etymwordnet_data = {}
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                # Skip header
                next(f)
                for line in f:
                    try:
                        parts = line.strip().split(',', 4)
                        if len(parts) >= 4:
                            lang, word, roots, year = parts[0], parts[1], parts[2], parts[3]
                            definition = parts[4] if len(parts) > 4 else ""
                            
                            if lang not in self.etymwordnet_data:
                                self.etymwordnet_data[lang] = {}
                                
                            self.etymwordnet_data[lang][word] = {
                                "roots": roots.split("|") if roots else [],
                                "year": int(year) if year and year.strip().lstrip('-').isdigit() else None,
                                "definition": definition
                            }
                    except Exception as e:
                        logger.error(f"Error parsing etymwordnet line: {line}, {str(e)}")
                        
            total_words = sum(len(words) for words in self.etymwordnet_data.values())
            logger.info(f"Loaded {total_words} words from Etymological Wordnet")
        except Exception as e:
            logger.error(f"Error loading etymwordnet data: {str(e)}")
            self.etymwordnet_data = {}
            
    def test_fetch_from_etymwordnet(self, word, language):
        """Test fetching from etymwordnet"""
        logger.info(f"Testing etymwordnet source for {word} ({language})")
        
        result = {
            "word": word,
            "language": language,
            "year": None,
            "definition": "",
            "roots": []
        }
        
        # Get language code
        lang_codes = {
            "English": "eng",
            "French": "fra",
            "Latin": "lat",
            "Ancient Greek": "grc"
        }
        lang_code = lang_codes.get(language)
        
        if not lang_code:
            logger.warning(f"Unknown language code for {language}")
            return result
            
        # Check if word exists in sample data
        word_lower = word.lower()
        if lang_code in self.etymwordnet_data and word_lower in self.etymwordnet_data[lang_code]:
            word_data = self.etymwordnet_data[lang_code][word_lower]
            logger.info(f"Found {word} in etymwordnet sample data")
            
            # Add year and definition
            if word_data.get("year"):
                result["year"] = word_data["year"]
            
            if word_data.get("definition"):
                result["definition"] = word_data["definition"]
            
            # Process roots
            for root_entry in word_data.get("roots", []):
                # Parse the root format (e.g., "grc:ἐτυμολογία")
                if ":" in root_entry:
                    root_lang_code, root_word = root_entry.split(":", 1)
                    lang_names = {v: k for k, v in lang_codes.items()}
                    target_lang = lang_names.get(root_lang_code, root_lang_code)
                    
                    root = {
                        "word": root_word,
                        "language": target_lang,
                        "year": None
                    }
                    
                    # Estimate year based on language
                    if target_lang == "Latin":
                        root["year"] = -100  # Classical Latin period
                    elif target_lang == "Ancient Greek":
                        root["year"] = -400  # Classical Greek period
                    elif target_lang == "Proto-Indo-European":
                        root["year"] = -4500  # Estimated PIE period
                    
                    result["roots"].append(root)
                    logger.info(f"Added root: {root_word} ({target_lang})")
        
        return result
        
    def run_tests(self):
        """Run tests on sample words"""
        logger.info("Starting tests")
        
        # Test etymwordnet source
        success_count = 0
        total_count = 0
        
        for language, words in self.test_words.items():
            for word in words:
                total_count += 1
                result = self.test_fetch_from_etymwordnet(word, language)
                if result and result.get("roots"):
                    success_count += 1
                    logger.info(f"✅ Successfully returned data for {word} ({language})")
                    logger.info(f"   Year: {result.get('year')}")
                    logger.info(f"   Definition: {result.get('definition')}")
                    logger.info(f"   Roots: {len(result.get('roots', []))} items")
                    for i, root in enumerate(result.get("roots", []), 1):
                        logger.info(f"   - Root {i}: {root.get('word')} ({root.get('language')})")
                else:
                    logger.warning(f"❌ Failed to return data for {word} ({language})")
        
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        logger.info(f"Tests completed: {success_count}/{total_count} successful ({success_rate:.1f}%)")

if __name__ == "__main__":
    test = EtymWordnetTest()
    test.run_tests() 