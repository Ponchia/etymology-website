#!/usr/bin/env python3
"""
Etymology System Demo Script

This script demonstrates the etymology generation system's capabilities.
It uses the sample words with interesting etymologies and shows the quality of data that can be generated.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add this file's directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_etymology_simple import SimpleEtymologyTester

def main():
    """Run the etymology demo."""
    print("\n" + "=" * 40)
    print("ETYMOLOGY GENERATION SYSTEM DEMO")
    print("=" * 40 + "\n")
    
    # Get interesting words
    interesting_words = [
        "etymology", "philosophy", "democracy", "computer", "biology", 
        "language", "psychology", "science", "mathematics", "astronomy"
    ]
    
    print(f"Demonstrating etymology generation for {len(interesting_words)} interesting words:")
    print(", ".join(interesting_words))
    print("\n" + "-" * 40 + "\n")
    
    # Initialize the tester
    tester = SimpleEtymologyTester()
    
    # Process each word
    start_time = time.time()
    
    for word in interesting_words:
        # Process the word (using sample data for demonstration)
        result = tester.process_word(word)
        
        # Print a formatted summary
        print_formatted_etymology(result)
        print("\n" + "-" * 40 + "\n")
    
    elapsed_time = time.time() - start_time
    
    # Print performance summary
    print(f"Processed {len(interesting_words)} words in {elapsed_time:.2f} seconds")
    print(f"Average time per word: {elapsed_time / len(interesting_words):.2f} seconds")
    print(f"Estimated processing rate: {len(interesting_words) / elapsed_time:.2f} words per second")
    
    # Estimate full dictionary processing
    english_dictionary_size = 171476  # Approximate
    
    print("\nEstimated processing times for full English dictionary:")
    for processes in [1, 4, 10]:
        estimated_time = (english_dictionary_size / len(interesting_words)) * elapsed_time / processes
        hours = estimated_time / 3600
        print(f"  With {processes} processes: {hours:.1f} hours")
    
    print("\n" + "=" * 40)
    print("END OF DEMO")
    print("=" * 40)

def print_formatted_etymology(etymology_data):
    """Print a nicely formatted etymology summary."""
    word = etymology_data.get("word", "Unknown")
    language = etymology_data.get("language", "Unknown")
    year = etymology_data.get("year")
    definition = etymology_data.get("definition", "")
    quality_score = etymology_data.get("quality_score", 0)
    
    # Word header with language and quality score
    print(f"📘 {word.upper()} ({language}) - Quality: {quality_score}/100")
    
    # Year and definition
    if year is not None:
        era = "BCE" if year < 0 else "CE"
        year_abs = abs(year)
        print(f"📅 Year: {year_abs} {era}")
    else:
        print("📅 Year: Unknown")
    
    if definition:
        print(f"📝 Definition: {definition}")
    else:
        print("📝 Definition: Not available")
    
    # Root words
    roots = etymology_data.get("roots", [])
    if roots:
        print(f"\n🌱 ROOT WORDS ({len(roots)}):")
        for i, root in enumerate(roots, 1):
            root_word = root.get("word", "Unknown")
            root_lang = root.get("language", "Unknown")
            root_year = root.get("year")
            root_def = root.get("definition", "")
            
            # Format year as BCE/CE
            if root_year is not None:
                era = "BCE" if root_year < 0 else "CE"
                root_year_abs = abs(root_year)
                year_str = f"{root_year_abs} {era}"
            else:
                year_str = "Unknown"
                
            print(f"  {i}. {root_word} ({root_lang}), Year: {year_str}")
            if root_def:
                print(f"     ↪ {root_def}")
    else:
        print("\n🌱 No root words found")

if __name__ == "__main__":
    main() 