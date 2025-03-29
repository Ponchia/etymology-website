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

class TestEtymologyGenerator(EtymologyGenerator):
    """A test version of the etymology generator that uses fixed word lists and saves output to a test directory"""
    
    def __init__(self, test_mode=True, threads=1, batch_size=5, save_output=False):
        super().__init__(test_mode=test_mode, threads=threads, batch_size=batch_size)
        self.save_output = save_output
        # Set a test output directory
        self.test_output_dir = Path("./test_output")
        if save_output and not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
    
    def fetch_word_lists(self):
        """Override to use test word lists"""
        logger.info("Using fixed test word lists")
        return TEST_WORDS
    
    def process_word(self, word: str, language: str) -> bool:
        """Process a single word and optionally save to test directory"""
        try:
            logger.info(f"Processing test word: {word} ({language})")
            
            # Fetch etymology data
            etymology_data = self.fetch_etymology(word, language)
            
            if not etymology_data:
                self.stats["failed_words"] += 1
                logger.info(f"No etymology data found for {word}")
                return False
            
            # Save to test directory if requested
            if self.save_output:
                file_path = self.test_output_dir / f"{language}_{word}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(etymology_data, f, indent=2)
                logger.info(f"Saved test output to {file_path}")
            
            # Print etymology summary
            self.print_etymology_summary(etymology_data)
            
            # Count connections
            root_count = len(etymology_data.get("roots", []))
            self.stats["total_connections"] += root_count
            
            # Update statistics
            self.stats["successful_words"] += 1
            self.stats["languages"][language] = self.stats["languages"].get(language, 0) + 1
            self.stats["last_processed"] = word
            self.stats["processed_words"].add(word)
            
            logger.info(f"Successfully processed {word} with {root_count} connections")
            return True
            
        except Exception as e:
            logger.error(f"Error processing word {word}: {str(e)}")
            self.stats["failed_words"] += 1
            return False
    
    def print_etymology_summary(self, etymology_data):
        """Print a summary of the etymology data for verification"""
        word = etymology_data.get("word", "unknown")
        language = etymology_data.get("language", "unknown")
        year = etymology_data.get("year", "unknown")
        definition = etymology_data.get("definition", "")
        roots = etymology_data.get("roots", [])
        
        logger.info(f"Etymology Summary for {word} ({language}), year: {year}")
        logger.info(f"Definition: {definition[:60]}...")
        
        if "meaning" in etymology_data:
            logger.info(f"Short meaning: {etymology_data['meaning']}")
        
        if roots:
            logger.info(f"Root words ({len(roots)}):")
            for i, root in enumerate(roots[:3]):  # Show first 3 roots
                root_word = root.get("word", "unknown")
                root_lang = root.get("language", "unknown")
                root_year = root.get("year", "unknown")
                logger.info(f"  {i+1}. {root_word} ({root_lang}), year: {root_year}")
            
            if len(roots) > 3:
                logger.info(f"  ...and {len(roots) - 3} more roots")
        else:
            logger.info("No root words found")

def main():
    # Create test generator in test mode with option to save output
    generator = TestEtymologyGenerator(
        test_mode=True,
        threads=2,
        batch_size=5,
        save_output=True
    )
    
    # Run the generator
    logger.info("Starting test run with fixed word lists")
    stats = generator.run()
    
    # Display results
    logger.info("Test run completed")
    logger.info(f"Words processed: {stats['total_words_processed']}")
    logger.info(f"Successful words: {stats['successful_words']}")
    logger.info(f"Failed words: {stats['failed_words']}")
    logger.info(f"Total connections: {stats['total_connections']}")
    
    return stats

if __name__ == "__main__":
    main() 