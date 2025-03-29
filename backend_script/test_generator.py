#!/usr/bin/env python3
import json
import logging
import os
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

class TestEtymologyGenerator(EtymologyGenerator):
    """A test version of the etymology generator that uses fixed word lists."""
    
    def __init__(self, test_mode=True, output_dir=None):
        """Initialize the test etymology generator."""
        self.output_dir = output_dir or Path("test_output")
        
        # Call the parent constructor
        super().__init__(test_mode=test_mode)
        
        # Set up test output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def fetch_word_lists(self):
        """Get fixed test word lists."""
        self.logger.info("Using fixed test word lists")
        
        # Define fixed test word lists for each language
        word_lists = {
            "English": ["etymology", "biology", "computer", "philosophy", "democracy"],
            "French": ["bonjour", "merci", "château", "fromage", "café"],
            "Latin": ["veni", "vidi", "vici", "aqua", "terra"],
            "Greek": ["logos", "cosmos", "pathos", "ethos", "chronos"]
        }
        
        return word_lists
    
    def process_word(self, word, language):
        """Process a word and evaluate its quality."""
        self.logger.info(f"Processing test word: {word} ({language})")
        
        # Call parent method to process the word
        success = super().process_word(word, language)
        
        if success:
            # Get the etymology data from the results dictionary
            key = f"{language}_{word}"
            etymology_data = self.results.get(key)
            
            if etymology_data:
                # Evaluate data quality
                quality_score = self.evaluate_data_quality(etymology_data, word, language)
                self.logger.info(f"Quality score for {word}: {quality_score}/100")
                
                # Save test output to file
                if self.output_dir:
                    file_path = self.output_dir / f"{language}_{word}.json"
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(etymology_data, f, indent=2)
                    self.logger.info(f"Saved test output to {file_path}")
                
                # Display etymology summary
                self.logger.info(f"Etymology Summary for {word} ({language}), year: {etymology_data.get('year')}")
                self.logger.info(f"Definition: {etymology_data.get('definition', '')[:50]}...")
                
                if "meaning" in etymology_data:
                    self.logger.info(f"Short meaning: {etymology_data.get('meaning', '')[:50]}")
                    
                roots = etymology_data.get("roots", [])
                if roots:
                    self.logger.info(f"Root words ({len(roots)}):")
                    for i, root in enumerate(roots, 1):
                        self.logger.info(f"  {i}. {root.get('word', '')} ({root.get('language', '')}), year: {root.get('year')}")
                else:
                    self.logger.info("No root words found")
                    
                self.logger.info(f"Successfully processed {word} with {len(roots)} connections")
                
                return True
        
        return False
    
    def evaluate_data_quality(self, etymology_data, word, language):
        """Evaluate the quality of etymology data and return a score out of 100."""
        # Initialize quality metrics if not already done
        if not hasattr(self, 'quality_scores'):
            self.quality_scores = []
            self.words_evaluated = 0
            self.words_with_roots = 0
            self.words_with_correct_year = 0
            self.words_with_expected_roots = 0
            self.words_with_expected_languages = 0
            self.words_with_definitions = 0
            self.invalid_roots = 0
            self.avg_quality_score = 0
        
        # Evaluate different aspects of the data
        score = 0
        max_score = 100
        
        # Check if we have reference data for this word
        word_key = word.lower()
        reference = REFERENCE_ETYMOLOGIES.get(word_key, {})
        
        # 1. Has roots (20 points)
        has_roots = False
        if 'roots' in etymology_data and etymology_data['roots']:
            score += 20
            has_roots = True
            self.words_with_roots += 1
        
        # 2. Has correct year (20 points)
        has_correct_year = False
        if reference and 'year' in reference and reference['year'] and 'year' in etymology_data and etymology_data['year']:
            ref_year = reference['year']
            word_year = etymology_data['year']
            
            # Allow a margin of error for years (wider for ancient languages)
            margin = 50
            if ref_year < 0:
                margin = 100  # Wider margin for ancient dates
                
            if abs(ref_year - word_year) <= margin:
                score += 20
                has_correct_year = True
                self.words_with_correct_year += 1
        
        # 3. Has expected roots (20 points)
        has_expected_roots = False
        if reference and 'expected_roots' in reference and reference['expected_roots']:
            # Check if any expected roots are present
            expected_roots = [r.lower() for r in reference['expected_roots']]
            found_roots = []
            
            if 'roots' in etymology_data:
                for root in etymology_data['roots']:
                    if 'word' in root:
                        root_word = root['word'].lower()
                        # Allow for partial matches (e.g. "philo" matches "philosophia")
                        for exp_root in expected_roots:
                            if exp_root in root_word or root_word in exp_root:
                                found_roots.append(exp_root)
            
            # Award points based on percentage of expected roots found
            if found_roots:
                percentage_found = len(set(found_roots)) / len(expected_roots)
                root_score = min(20, int(20 * percentage_found))
                score += root_score
                has_expected_roots = True
                self.words_with_expected_roots += 1
        
        # 4. Has expected languages (20 points)
        has_expected_languages = False
        if reference and 'expected_languages' in reference and reference['expected_languages']:
            expected_langs = [lang.lower() for lang in reference['expected_languages']]
            found_langs = []
            
            if 'roots' in etymology_data:
                for root in etymology_data['roots']:
                    if 'language' in root:
                        root_lang = root['language'].lower()
                        # Allow for language variant matches (e.g. "Old French" matches "French")
                        for exp_lang in expected_langs:
                            if exp_lang in root_lang or root_lang in exp_lang:
                                found_langs.append(exp_lang)
            
            # Award points based on percentage of expected languages found
            if found_langs:
                percentage_found = len(set(found_langs)) / len(expected_langs)
                lang_score = min(20, int(20 * percentage_found))
                score += lang_score
                has_expected_languages = True
                self.words_with_expected_languages += 1
        
        # 5. Has sensible definition (20 points)
        has_definition = False
        if 'definition' in etymology_data and etymology_data['definition'] and len(etymology_data['definition']) > 10:
            score += 20
            has_definition = True
            self.words_with_definitions += 1
        
        # 6. Check for invalid/blank root words
        if 'roots' in etymology_data:
            for root in etymology_data['roots']:
                if not root.get('word') or not root.get('language'):
                    self.invalid_roots += 1
                    score -= 10  # Penalty for invalid roots
        
        # Update quality metrics
        self.quality_scores.append(score)
        self.words_evaluated += 1
        self.avg_quality_score = sum(self.quality_scores) / len(self.quality_scores)
        
        return score
    
    def calculate_average_quality_score(self):
        """Calculate the average quality score across all processed words"""
        word_count = self.stats["successful_words"]
        if word_count == 0:
            return 0
        
        total_score = self.quality_scores["total_score"]
        return total_score / word_count
    
    def print_quality_report(self):
        """Print a comprehensive quality report"""
        word_count = self.stats["successful_words"]
        if word_count == 0:
            logger.info("No words processed, cannot generate quality report")
            return
        
        avg_score = self.calculate_average_quality_score()
        
        logger.info("\n===== DATA QUALITY REPORT =====")
        logger.info(f"Average quality score: {avg_score:.2f}/100")
        logger.info(f"Words with roots: {self.quality_scores['words_with_roots']} ({(self.quality_scores['words_with_roots']/word_count)*100:.1f}%)")
        logger.info(f"Words with correct year: {self.quality_scores['words_with_correct_year']} ({(self.quality_scores['words_with_correct_year']/word_count)*100:.1f}%)")
        logger.info(f"Words with expected roots: {self.quality_scores['words_with_expected_roots']} ({(self.quality_scores['words_with_expected_roots']/word_count)*100:.1f}%)")
        logger.info(f"Words with expected languages: {self.quality_scores['words_with_expected_languages']} ({(self.quality_scores['words_with_expected_languages']/word_count)*100:.1f}%)")
        logger.info(f"Words with sensible definitions: {self.quality_scores['words_with_sensible_definition']} ({(self.quality_scores['words_with_sensible_definition']/word_count)*100:.1f}%)")
        logger.info(f"Invalid root words detected: {self.quality_scores['invalid_roots']}")
        logger.info("=============================\n")
        
        # Data quality rating
        if avg_score >= 90:
            logger.info("QUALITY RATING: EXCELLENT")
        elif avg_score >= 75:
            logger.info("QUALITY RATING: GOOD")
        elif avg_score >= 50:
            logger.info("QUALITY RATING: FAIR")
        else:
            logger.info("QUALITY RATING: POOR")

def main():
    """Run the etymology test generator and evaluate results."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('test_generator')
    logger.info("Starting test run with fixed word lists")
    
    # Create test generator instance
    generator = TestEtymologyGenerator(
        test_mode=True,
        output_dir=Path("test_output")
    )
    
    # Run generator
    stats = generator.run()
    
    # Log results
    logger.info("Test run completed")
    
    if stats:
        logger.info(f"Words processed: {stats['words_processed']}")
        logger.info(f"Successful words: {stats['successful_words']}")
        logger.info(f"Failed words: {stats['failed_words']}")
        logger.info(f"Total connections: {stats['connections']}")
        
        # Output quality report
        logger.info("\n===== DATA QUALITY REPORT =====")
        logger.info(f"Average quality score: {generator.avg_quality_score:.2f}/100")
        logger.info(f"Words with roots: {generator.words_with_roots} ({(generator.words_with_roots / generator.words_evaluated * 100):.1f}%)")
        logger.info(f"Words with correct year: {generator.words_with_correct_year} ({(generator.words_with_correct_year / generator.words_evaluated * 100):.1f}%)")
        logger.info(f"Words with expected roots: {generator.words_with_expected_roots} ({(generator.words_with_expected_roots / generator.words_evaluated * 100):.1f}%)")
        logger.info(f"Words with expected languages: {generator.words_with_expected_languages} ({(generator.words_with_expected_languages / generator.words_evaluated * 100):.1f}%)")
        logger.info(f"Words with sensible definitions: {generator.words_with_definitions} ({(generator.words_with_definitions / generator.words_evaluated * 100):.1f}%)")
        logger.info(f"Invalid root words detected: {generator.invalid_roots}")
        logger.info("=============================\n")
        
        # Calculate quality rating
        if generator.avg_quality_score >= 80:
            quality_rating = "EXCELLENT"
        elif generator.avg_quality_score >= 60:
            quality_rating = "GOOD"
        elif generator.avg_quality_score >= 40:
            quality_rating = "FAIR"
        else:
            quality_rating = "POOR"
            
        logger.info(f"QUALITY RATING: {quality_rating}")
    else:
        logger.error("Test run failed to return statistics")

if __name__ == "__main__":
    main() 