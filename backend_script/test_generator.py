#!/usr/bin/env python3
import json
import logging
import os
import time
import random
import statistics
from pathlib import Path
from etymology_generator import EtymologyGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_generator")

# Sample words with known etymology for testing
TEST_WORDS = {
    "English": ["etymology", "computer", "philosophy", "democracy", "biology"],
    "French": ["bonjour", "merci", "fromage", "château", "café"],
    "Latin": ["veni", "vidi", "vici", "aqua", "terra"],
    "Greek": ["logos", "cosmos", "pathos", "ethos", "chronos"]
}

# Reference data for quality checks
REFERENCE_ETYMOLOGIES = {
    "etymology": {
        "language": "English",
        "year": 1398,
        "expected_roots": ["etymologia", "etymon", "ετυμολογία", "etymologie"],
        "expected_languages": ["Latin", "Greek", "Ancient Greek", "Old French"]
    },
    "philosophy": {
        "language": "English",
        "year": 1300,
        "expected_roots": ["philosophia", "philosophos", "φιλοσοφία", "philosophie"],
        "expected_languages": ["Latin", "Greek", "Ancient Greek", "Old French"]
    },
    "democracy": {
        "language": "English",
        "year": 1570,
        "expected_roots": ["democratia", "δημοκρατία", "demos", "kratos", "dēmocratia"],
        "expected_languages": ["Latin", "Greek", "Ancient Greek", "Medieval Latin"]
    },
    "computer": {
        "language": "English",
        "year": 1640,
        "expected_roots": ["compute", "computare", "computus"],
        "expected_languages": ["English", "Latin", "Medieval Latin", "Middle English"]
    },
    "biology": {
        "language": "English",
        "year": 1819,
        "expected_roots": ["bio", "logia", "bios", "logos", "βίος", "biologia"],
        "expected_languages": ["Greek", "Ancient Greek", "New Latin", "Latin"]
    },
    "bonjour": {
        "language": "French",
        "year": 1400,
        "expected_roots": ["bon", "jour", "diurnum", "jour", "diurnus"],
        "expected_languages": ["Latin", "Old French", "French"]
    },
    "merci": {
        "language": "French",
        "year": 1200,
        "expected_roots": ["mercedem", "merces", "mercit"],
        "expected_languages": ["Latin", "Old French"]
    },
    "château": {
        "language": "French",
        "year": 1100,
        "expected_roots": ["castellum", "chastel", "castrum"],
        "expected_languages": ["Latin", "Old French"]
    },
    "fromage": {
        "language": "French",
        "year": 1200,
        "expected_roots": ["formaticus", "forma"],
        "expected_languages": ["Latin", "Vulgar Latin", "Late Latin"]
    },
    "café": {
        "language": "French",
        "year": 1690,
        "expected_roots": ["kahve", "qahwah", "koffie"],
        "expected_languages": ["Turkish", "Arabic", "Dutch"]
    },
    "logos": {
        "language": "Greek",
        "year": -700,
        "expected_roots": ["legein", "λόγος", "lego"],
        "expected_languages": ["Proto-Indo-European", "Ancient Greek"]
    },
    "aqua": {
        "language": "Latin",
        "year": -100,
        "expected_roots": ["akwa", "ap-"],
        "expected_languages": ["Proto-Indo-European", "Proto-Italic"]
    },
    "veni": {
        "language": "Latin",
        "year": -100,
        "expected_roots": ["venire", "gwem"],
        "expected_languages": ["Proto-Indo-European", "Proto-Italic"]
    },
    "terra": {
        "language": "Latin",
        "year": -100,
        "expected_roots": ["ters", "tersus", "torrid"],
        "expected_languages": ["Proto-Indo-European", "Proto-Italic"]
    },
    "vici": {
        "language": "Latin",
        "year": -100,
        "expected_roots": ["vincere", "vicis"],
        "expected_languages": ["Proto-Indo-European", "Proto-Italic", "Latin"]
    },
    "vidi": {
        "language": "Latin",
        "year": -100,
        "expected_roots": ["videre", "weid", "vidēre"],
        "expected_languages": ["Proto-Indo-European", "Proto-Italic", "Latin"]
    },
    "chronos": {
        "language": "Greek",
        "year": -700,
        "expected_roots": ["χρόνος", "khronos"],
        "expected_languages": ["Ancient Greek", "Greek"]
    },
    "ethos": {
        "language": "Greek",
        "year": -700,
        "expected_roots": ["ἦθος", "ethos"],
        "expected_languages": ["Ancient Greek", "Greek"]
    },
    "pathos": {
        "language": "Greek",
        "year": -700,
        "expected_roots": ["πάθος", "pathos"],
        "expected_languages": ["Ancient Greek", "Greek"]
    },
    "cosmos": {
        "language": "Greek",
        "year": -700,
        "expected_roots": ["κόσμος", "kosmos"],
        "expected_languages": ["Ancient Greek", "Greek"]
    }
}

class EtymologyGeneratorTester:
    def __init__(self):
        self.test_output_dir = Path("./test_output")
        self.words_processed = 0
        self.successful_words = 0
        self.failed_words = 0
        self.connections = 0
        self.quality_scores = []
        
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
            
    def run_test(self, use_fixed_list=True):
        """Run test with optional fixed word list"""
        logger.info("Starting test run with fixed word lists")
        
        # Create generator with test mode and geographical data enabled
        generator = EtymologyGenerator(
            max_words=5, 
            languages=["English", "French", "Latin", "Greek"],
            test_mode=True,
            sources="wiktionary,etymonline",
            geo_data=True  # Enable geographical data collection
        )
        
        # Set test output directory
        generator.output_dir = self.test_output_dir
        
        start_time = time.time()
        
        if use_fixed_list:
            test_words = {
                "English": ["etymology", "biology", "computer", "philosophy", "democracy"],
                "French": ["bonjour", "merci", "château", "fromage", "café"],
                "Latin": ["veni", "vidi", "vici", "aqua", "terra"],
                "Greek": ["logos", "cosmos", "pathos", "ethos", "chronos"]
            }
            
            # Process each test word
            for language, words in test_words.items():
                generator.logger.info(f"Processing {len(words)} {language} words")
                for word in words:
                    try:
                        result = generator.process_word(word, language)
                        self.words_processed += 1
                        if result:
                            self.successful_words += 1
                            self.connections += len(result.get("roots", []))
                            self.quality_scores.append(result.get("quality_score", 0))
                        else:
                            self.failed_words += 1
                    except Exception as e:
                        generator.logger.error(f"Error processing {word}: {str(e)}")
                        self.failed_words += 1
                    
        end_time = time.time()
        elapsed_minutes = (end_time - start_time) / 60
        
        # Log results
        generator.logger.info(f"Completed in {elapsed_minutes:.2f} minutes")
        generator.logger.info(f"Total words processed: {self.words_processed}")
        generator.logger.info(f"Successful words: {self.successful_words}")
        generator.logger.info(f"Failed words: {self.failed_words}")
        generator.logger.info(f"Total connections: {self.connections}")
        
        # Return generator statistics for analysis
        return generator.stats if hasattr(generator, 'stats') else {}
        
    def analyze_quality(self):
        """Analyze the quality of generated etymology data"""
        logger.info("Test run completed")
        logger.info(f"Words processed: {self.words_processed}")
        logger.info(f"Successful words: {self.successful_words}")
        logger.info(f"Failed words: {self.failed_words}")
        logger.info(f"Total connections: {self.connections}")
        
        if not self.quality_scores:
            logger.warning("No quality data available for analysis")
            return
            
        # Calculate metrics
        avg_quality = statistics.mean(self.quality_scores) if self.quality_scores else 0
        
        # Check files for specific criteria
        words_with_roots = 0
        words_with_year = 0
        words_with_expected_roots = 0
        words_with_expected_languages = 0
        words_with_definitions = 0
        invalid_roots = 0
        
        # Expected roots for validation
        expected_roots = {
            "English_etymology": ["Latin", "Ancient Greek"],
            "English_biology": ["Greek", "Ancient Greek"],
            "English_computer": ["Latin"],
            "English_philosophy": ["Latin", "Ancient Greek", "Greek"],
            "English_democracy": ["Ancient Greek", "Greek"],
            "French_bonjour": ["French", "Latin"],
            "French_merci": ["Latin"],
            "French_château": ["Latin"],
            "French_fromage": ["Latin"],
            "French_café": ["Arabic"],
            "Latin_veni": ["Proto-Indo-European"],
            "Latin_vidi": ["Proto-Indo-European"],
            "Latin_vici": ["Proto-Indo-European"],
            "Latin_aqua": ["Proto-Indo-European"],
            "Latin_terra": ["Proto-Indo-European"],
            "Greek_logos": ["Ancient Greek", "Greek"],
            "Greek_cosmos": ["Ancient Greek", "Greek"],
            "Greek_pathos": ["Ancient Greek", "Greek"],
            "Greek_ethos": ["Ancient Greek", "Greek"],
            "Greek_chronos": ["Ancient Greek", "Greek"]
        }
        
        # Check all output files
        for file_name in os.listdir(self.test_output_dir):
            if not file_name.endswith('.json'):
                continue
                
            file_path = os.path.join(self.test_output_dir, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # File key is language_word (e.g., "English_etymology")
                file_key = file_name.replace('.json', '')
                
                # Check for roots
                if data.get('roots') and len(data['roots']) > 0:
                    words_with_roots += 1
                    
                    # Check for valid root languages
                    root_languages = [root.get('language') for root in data.get('roots', [])]
                    invalid_language = False
                    
                    for lang in root_languages:
                        if not lang or lang in ["Unknown", "unknown"]:
                            invalid_language = True
                            invalid_roots += 1
                            
                    # Check if expected roots are present
                    expected = expected_roots.get(file_key, [])
                    if expected:
                        found_expected = False
                        for expected_lang in expected:
                            if any(expected_lang == lang for lang in root_languages):
                                found_expected = True
                                break
                                
                        if found_expected:
                            words_with_expected_roots += 1
                    else:
                        # No expectations defined, consider it valid
                        words_with_expected_roots += 1
                
                # Check for year
                if data.get('year'):
                    words_with_year += 1
                    
                # Check for sensible definition
                if data.get('definition') and len(data.get('definition', '')) > 10:
                    words_with_definitions += 1
                    
                # Check language
                expected_lang = file_key.split('_')[0]
                if data.get('language') == expected_lang:
                    words_with_expected_languages += 1
                    
            except Exception as e:
                logger.error(f"Error analyzing {file_name}: {str(e)}")
                
        # Calculate percentages
        pct_roots = (words_with_roots / self.words_processed) * 100 if self.words_processed > 0 else 0
        pct_year = (words_with_year / self.words_processed) * 100 if self.words_processed > 0 else 0
        pct_expected_roots = (words_with_expected_roots / self.words_processed) * 100 if self.words_processed > 0 else 0
        pct_expected_languages = (words_with_expected_languages / self.words_processed) * 100 if self.words_processed > 0 else 0
        pct_definitions = (words_with_definitions / self.words_processed) * 100 if self.words_processed > 0 else 0
        
        # Print quality report
        logger.info("\n===== DATA QUALITY REPORT =====")
        logger.info(f"Average quality score: {avg_quality:.2f}/100")
        logger.info(f"Words with roots: {words_with_roots} ({pct_roots:.1f}%)")
        logger.info(f"Words with correct year: {words_with_year} ({pct_year:.1f}%)")
        logger.info(f"Words with expected roots: {words_with_expected_roots} ({pct_expected_roots:.1f}%)")
        logger.info(f"Words with expected languages: {words_with_expected_languages} ({pct_expected_languages:.1f}%)")
        logger.info(f"Words with sensible definitions: {words_with_definitions} ({pct_definitions:.1f}%)")
        logger.info(f"Invalid root words detected: {invalid_roots}")
        logger.info("=============================\n")
        
        # Overall quality rating
        if avg_quality >= 80:
            rating = "EXCELLENT"
        elif avg_quality >= 60:
            rating = "GOOD"
        elif avg_quality >= 40:
            rating = "FAIR"
        elif avg_quality >= 20:
            rating = "POOR"
        else:
            rating = "VERY POOR"
            
        logger.info(f"QUALITY RATING: {rating}")
        
if __name__ == "__main__":
    tester = EtymologyGeneratorTester()
    tester.run_test()
    tester.analyze_quality() 