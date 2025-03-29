#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import argparse
import multiprocessing
from pathlib import Path
from functools import partial
from datetime import datetime

# Add this file's directory to the path so we can import the tester module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_etymology_simple import SimpleEtymologyTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("etymology_generator")

class EtymologyGenerator:
    """A system to generate etymology data for a list of words."""
    
    def __init__(self, output_dir="output", use_sample_data=False, store_by_first_letter=False):
        """Initialize the generator with output directory."""
        # Set up paths
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Progress and summary files
        self.progress_file = self.output_dir / "progress.json"
        self.summary_file = self.output_dir / "summary.json"
        
        # Tester to get etymology data
        self.tester = SimpleEtymologyTester()
        
        # Statistics
        self.stats = {
            "total_words": 0,
            "processed_words": 0,
            "start_time": time.time(),
            "end_time": None,
            "quality_scores": [],
            "connections": 0
        }
        
        # Flags
        self.use_sample_data = use_sample_data
        self.store_by_first_letter = store_by_first_letter
        
        # Load progress if it exists
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load progress from a progress file if it exists."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    logger.info(f"Loaded progress: {progress['processed_words']} of {progress['total_words']} words processed")
                    
                    # Update statistics
                    self.stats.update({
                        "total_words": progress.get("total_words", 0),
                        "processed_words": progress.get("processed_words", 0),
                        "start_time": progress.get("start_time", time.time()),
                        "quality_scores": progress.get("quality_scores", []),
                        "connections": progress.get("connections", 0)
                    })
                    
                    return progress
            except Exception as e:
                logger.error(f"Error loading progress: {str(e)}")
        
        return {
            "total_words": 0,
            "processed_words": 0,
            "processed_batches": [],
            "start_time": time.time()
        }
    
    def save_progress(self):
        """Save progress to a file."""
        self.progress.update({
            "total_words": self.stats["total_words"],
            "processed_words": self.stats["processed_words"],
            "quality_scores": self.stats["quality_scores"],
            "connections": self.stats["connections"],
            "last_update": time.time()
        })
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2)
        
        logger.info(f"Saved progress: {self.stats['processed_words']} of {self.stats['total_words']} words processed")
    
    def save_summary(self):
        """Save summary statistics to a file."""
        # Calculate final statistics
        self.stats["end_time"] = time.time()
        elapsed_time = self.stats["end_time"] - self.stats["start_time"]
        words_per_second = self.stats["processed_words"] / elapsed_time if elapsed_time > 0 else 0
        
        avg_quality = sum(self.stats["quality_scores"]) / len(self.stats["quality_scores"]) if self.stats["quality_scores"] else 0
        avg_connections = self.stats["connections"] / self.stats["processed_words"] if self.stats["processed_words"] > 0 else 0
        
        summary = {
            "total_words": self.stats["total_words"],
            "processed_words": self.stats["processed_words"],
            "elapsed_time": elapsed_time,
            "words_per_second": words_per_second,
            "average_quality_score": avg_quality,
            "total_connections": self.stats["connections"],
            "average_connections_per_word": avg_connections,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved summary to {self.summary_file}")
        
        # Print summary
        print("\n=== Etymology Generation Summary ===")
        print(f"Processed {self.stats['processed_words']} words in {elapsed_time:.3f} seconds")
        print(f"Processing rate: {words_per_second:.1f} words per second")
        print(f"Average quality score: {avg_quality:.1f}/100")
        print(f"Total connections made: {self.stats['connections']}")
        print(f"Average connections per word: {avg_connections:.1f}")
        
        if self.stats["processed_words"] < self.stats["total_words"]:
            remaining_words = self.stats["total_words"] - self.stats["processed_words"]
            estimated_remaining_time = remaining_words / words_per_second if words_per_second > 0 else 0
            print(f"\nRemaining words: {remaining_words}")
            print(f"Estimated time to complete: {estimated_remaining_time:.1f} seconds")
        
        print("=" * 40)
    
    def load_word_list(self, word_list_file):
        """Load a list of words from a file."""
        try:
            with open(word_list_file, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
            
            self.stats["total_words"] = len(words)
            logger.info(f"Loaded {len(words)} words from {word_list_file}")
            return words
        except Exception as e:
            logger.error(f"Error loading word list: {str(e)}")
            return []
    
    def process_batch(self, batch, batch_index, total_batches, language="English"):
        """Process a batch of words and save the results."""
        batch_size = len(batch)
        batch_start_time = time.time()
        
        logger.info(f"Processing batch {batch_index + 1}/{total_batches} with {batch_size} words")
        
        results = {}
        by_letter_results = {}
        connections = 0
        quality_scores = []
        
        for word in batch:
            # Process the word
            if self.use_sample_data and word.lower() in self.tester.sample_data:
                result = self.tester.sample_data[word.lower()]
                logger.info(f"Using sample data for {word}")
            else:
                result = self.tester.process_word(word, language)
            
            results[word] = result
            
            # Store by first letter if enabled
            if self.store_by_first_letter and word:
                first_letter = word[0].lower()
                if first_letter.isalpha():
                    if first_letter not in by_letter_results:
                        by_letter_results[first_letter] = {}
                    by_letter_results[first_letter][word] = result
            
            # Update statistics
            quality_scores.append(result.get("quality_score", 0))
            connections += len(result.get("roots", []))
        
        # Save batch results
        if self.store_by_first_letter:
            # Save each letter's results to its own directory
            for letter, letter_results in by_letter_results.items():
                letter_dir = self.output_dir / letter
                os.makedirs(letter_dir, exist_ok=True)
                
                for word, result in letter_results.items():
                    word_file = letter_dir / f"{word}.json"
                    with open(word_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                
                logger.info(f"Saved {len(letter_results)} words in directory {letter_dir}")
        else:
            # Save all batch results to a single file
            batch_file = self.output_dir / f"batch_{batch_index + 1}_of_{total_batches}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        
        batch_elapsed_time = time.time() - batch_start_time
        batch_wps = batch_size / batch_elapsed_time if batch_elapsed_time > 0 else 0
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        avg_connections = connections / batch_size if batch_size > 0 else 0
        
        logger.info(f"Completed batch {batch_index + 1}/{total_batches} in {batch_elapsed_time:.2f}s")
        logger.info(f"Batch stats: {batch_wps:.1f} words/s, Quality: {avg_quality:.1f}/100, Connections: {connections}")
        
        return {
            "batch_index": batch_index,
            "words_processed": batch_size,
            "connections": connections,
            "quality_scores": quality_scores,
            "elapsed_time": batch_elapsed_time
        }
    
    def update_stats(self, batch_result):
        """Update overall statistics with batch results."""
        self.stats["processed_words"] += batch_result["words_processed"]
        self.stats["connections"] += batch_result["connections"]
        self.stats["quality_scores"].extend(batch_result["quality_scores"])
        
        # Update progress
        self.progress["processed_words"] = self.stats["processed_words"]
        self.progress["processed_batches"].append(batch_result["batch_index"])
        
        # Save progress
        self.save_progress()
        
        # Print progress
        total_elapsed = time.time() - self.stats["start_time"]
        progress_percent = (self.stats["processed_words"] / self.stats["total_words"]) * 100 if self.stats["total_words"] > 0 else 0
        wps = self.stats["processed_words"] / total_elapsed if total_elapsed > 0 else 0
        
        logger.info(f"Overall progress: {progress_percent:.1f}% ({self.stats['processed_words']}/{self.stats['total_words']})")
        logger.info(f"Overall speed: {wps:.1f} words/s")
        
        if self.stats["processed_words"] < self.stats["total_words"]:
            remaining_words = self.stats["total_words"] - self.stats["processed_words"]
            remaining_time = remaining_words / wps if wps > 0 else 0
            remaining_hours = remaining_time / 3600
            logger.info(f"Estimated time remaining: {remaining_time:.1f}s ({remaining_hours:.2f} hours)")
    
    def run(self, word_list, batch_size=100, num_processes=1, language="English"):
        """Process all words in the list using multiprocessing for efficiency."""
        if not word_list:
            logger.warning("No words to process")
            return
        
        # Update total words count
        self.stats["total_words"] = len(word_list)
        
        # Skip words that were already processed
        if self.progress.get("processed_batches"):
            processed_batches = set(self.progress["processed_batches"])
        else:
            processed_batches = set()
        
        # Calculate batches
        num_batches = (len(word_list) + batch_size - 1) // batch_size
        batches = []
        
        for i in range(num_batches):
            if i not in processed_batches:
                start_idx = i * batch_size
                end_idx = min(start_idx + batch_size, len(word_list))
                batches.append((word_list[start_idx:end_idx], i, num_batches))
        
        logger.info(f"Processing {len(batches)} batches of {batch_size} words each, using {num_processes} processes")
        
        if not batches:
            logger.info("All batches already processed")
            self.save_summary()
            return
        
        # Process batches
        if num_processes > 1 and len(batches) > 1:
            # Use multiprocessing
            process_func = partial(self._process_batch_wrapper, language=language)
            
            with multiprocessing.Pool(processes=num_processes) as pool:
                for batch_result in pool.starmap(process_func, batches):
                    self.update_stats(batch_result)
        else:
            # Process sequentially
            for batch, batch_idx, total_batches in batches:
                batch_result = self.process_batch(batch, batch_idx, total_batches, language)
                self.update_stats(batch_result)
        
        # Save final summary
        self.save_summary()
    
    def _process_batch_wrapper(self, batch, batch_index, total_batches, language="English"):
        """Wrapper for process_batch to be used with multiprocessing."""
        # Create a new tester instance for this process
        tester = SimpleEtymologyTester()
        self.tester = tester
        
        return self.process_batch(batch, batch_index, total_batches, language)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate etymology data for a list of words')
    parser.add_argument('--word-list', type=str, required=True, help='Path to the word list file')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory for output files')
    parser.add_argument('--batch-size', type=int, default=20, help='Number of words to process in each batch')
    parser.add_argument('--processes', type=int, default=1, help='Number of processes to use')
    parser.add_argument('--language', type=str, default='English', help='Language of the word list')
    parser.add_argument('--use-sample', action='store_true', help='Use sample data for known words')
    parser.add_argument('--store-by-first-letter', action='store_true', help='Store words in directories by first letter')
    
    return parser.parse_args()

def main():
    """Main entry point for the etymology generator."""
    args = parse_arguments()
    
    # Create the generator
    generator = EtymologyGenerator(
        output_dir=args.output_dir,
        use_sample_data=args.use_sample,
        store_by_first_letter=args.store_by_first_letter
    )
    
    # Load the word list
    word_list = generator.load_word_list(args.word_list)
    
    if not word_list:
        logger.error("No words loaded. Exiting.")
        return 1
    
    try:
        # Run the generator
        generator.run(
            word_list=word_list,
            batch_size=args.batch_size,
            num_processes=args.processes,
            language=args.language
        )
        
        # Save summary
        generator.save_summary()
        
        return 0
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        generator.save_progress()
        generator.save_summary()
        return 2
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        generator.save_progress()
        return 1

if __name__ == "__main__":
    main() 