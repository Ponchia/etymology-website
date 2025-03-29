#!/usr/bin/env python3
import os
import sys
import argparse
import random
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create a dictionary file for testing")
    
    parser.add_argument("--output", "-o", type=str, default="test_dict.txt",
                      help="Path to output dictionary file (default: test_dict.txt)")
    
    parser.add_argument("--words", "-n", type=int, default=20,
                      help="Number of words to include in the dictionary (default: 20)")
    
    parser.add_argument("--full", action="store_true",
                      help="Use the full dictionary instead of the common words (slower)")
    
    parser.add_argument("--random", action="store_true",
                      help="Randomly select words from the dictionary")
    
    parser.add_argument("--seed", type=int, default=42,
                      help="Random seed for reproducibility (default: 42)")
    
    return parser.parse_args()

def get_common_words():
    """Return a list of common English words."""
    common_words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at"
    ]
    return common_words

def get_etymological_words():
    """Return a list of words with interesting etymology."""
    interesting_words = [
        "democracy", "philosophy", "etymology", "computer", "biology",
        "language", "psychology", "science", "mathematics", "astronomy"
    ]
    return interesting_words

def create_dictionary(output_file, num_words=20, use_full=False, random_select=False, seed=42):
    """Create a dictionary file with the specified number of words."""
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Create output directory if needed
    output_path = Path(output_file)
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Select words
    if use_full:
        # If we want the full dictionary, try to load it or fall back to common words
        try:
            with open("/usr/share/dict/words", "r") as f:
                all_words = [line.strip() for line in f if len(line.strip()) > 2]
            
            print(f"Loaded {len(all_words)} words from system dictionary")
            
            if random_select:
                words = random.sample(all_words, min(num_words, len(all_words)))
            else:
                words = all_words[:num_words]
        except FileNotFoundError:
            print("System dictionary not found, using common words instead")
            words = get_common_words()
    else:
        if random_select:
            # Get a mix of common and etymologically interesting words
            words = get_common_words() + get_etymological_words()
            words = random.sample(words, min(num_words, len(words)))
        else:
            words = get_common_words()[:num_words]
    
    # Write the dictionary
    with open(output_file, "w") as f:
        for word in words:
            f.write(word + "\n")
    
    print(f"Created dictionary with {len(words)} words at {output_file}")
    return words

def main():
    args = parse_arguments()
    
    words = create_dictionary(
        output_file=args.output,
        num_words=args.words,
        use_full=args.full,
        random_select=args.random,
        seed=args.seed
    )
    
    # Print a sample of the words
    sample_size = min(10, len(words))
    print(f"Sample words: {', '.join(words[:sample_size])}")
    
    if len(words) > sample_size:
        print(f"... and {len(words) - sample_size} more")

if __name__ == "__main__":
    main() 