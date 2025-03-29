# Etymology Website Project

A system for generating and visualizing etymology data for English words.

## Project Structure

```
etymology-website/
├── backend_script/          # Backend scripts for etymology data generation
│   ├── test_etymology_simple.py     # Simplified etymology tester
│   ├── generate_etymology.py        # Main etymology generator
│   ├── create_dictionary.py         # Dictionary creation tool
│   ├── etymology_generator.py       # Original etymology generator (work in progress)
│   └── cache/                       # Cache for web requests
│       ├── wiktionary/              # Wiktionary cache
│       ├── etymonline/              # Etymonline cache
│       └── test_cache/              # Test cache
├── data/                    # Data directory
│   └── words/                       # Word lists and dictionary files
└── frontend/                # Frontend code (future development)
```

## Usage

All scripts are located in the `backend_script` directory:

### Quick Start with Interactive Menu

The simplest way to use the system is with the interactive menu:

```bash
./run.sh
```

This provides an easy-to-use menu for running all available tools.

### Create a Dictionary

```bash
cd backend_script
python create_dictionary.py --output data/test_dict.txt --words 20
```

Options:
- `--output`, `-o`: Output file path (default: test_dict.txt)
- `--words`, `-n`: Number of words to include (default: 20)
- `--full`: Use full dictionary instead of common words
- `--random`: Randomly select words
- `--seed`: Random seed (default: 42)

### Generate Etymology Data

```bash
cd backend_script
python generate_etymology.py --word-list data/test_dict.txt --processes 4 --output-dir data/etymology_output
```

Options:
- `--word-list`, `-w`: Path to word list file (required)
- `--batch-size`, `-b`: Words per batch (default: 100)
- `--processes`, `-p`: Number of parallel processes (default: 1)
- `--output-dir`, `-o`: Output directory (default: etymology_output)
- `--language`, `-l`: Language of words (default: English)
- `--use-sample`, `-s`: Use sample data for known words

### Run Simple Test

```bash
cd backend_script
python test_etymology_simple.py
```

This runs a simplified test on a predefined set of words.

### Run Interactive Demo

```bash
cd backend_script
python demo.py
```

This demo script showcases the etymology generation system with nicely formatted output for 10 interesting words. It demonstrates the quality of data that can be generated and provides performance metrics.

## Features

- Fetches etymology data from multiple sources:
  - Wiktionary
  - Etymonline
- Processes and merges data to create comprehensive etymology information
- Scores etymology quality on a scale of 0-100
- Supports parallel processing for efficient generation
- Implements caching to reduce load on data sources
- Provides resumable batch processing with progress tracking

## Data Structure

The generated data is saved in JSON format with the following structure:

```json
{
  "word": "etymology",
  "language": "English",
  "year": 1398,
  "definition": "The study of the origin of words and the way in which their meanings have changed throughout history",
  "roots": [
    {
      "word": "etymologia",
      "language": "Latin",
      "year": 100,
      "definition": "Analysis of a word to find its true meaning"
    },
    {
      "word": "ἐτυμολογία",
      "language": "Greek",
      "year": -400,
      "definition": "From ἔτυμον (étymon, 'true sense') + -λογία (-logía, 'study of')"
    }
  ],
  "quality_score": 95
}
```

## Performance

- Sample data processing: ~62 words per second
- Real data processing: ~1.67 words per second
- Parallel processing with 4 processes: ~4x speedup

## Future Development

- Improve HTML parsing for more accurate data extraction
- Add more etymology data sources
- Optimize web scraping with asynchronous requests
- Create visualization tools for etymology connections
- Develop a web frontend for the etymology database
- Implement a database for storing the etymology data
- Create a REST API for accessing the data
- Apply machine learning techniques to improve data extraction

## Requirements

- Python 3.6+
- Required packages (install with `pip install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - argparse 