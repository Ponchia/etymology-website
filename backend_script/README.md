# Etymology Dataset Generator

This script automates the generation of etymology data for the Etymology Website project.

## Features

- Fetches words from multiple language sources
- Extracts etymology data from Wiktionary, EtymOnline, and other sources
- Saves data in the required JSON format for the Etymology Website
- Tracks progress and can resume from where it left off
- Test mode to verify functionality without writing files
- Multi-threaded processing for improved performance

## Requirements

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Standard Run

To run the etymology generator normally:

```bash
python etymology_generator.py
```

### Test Mode

To run in test mode (no file writing):

```bash
python etymology_generator.py --test
```

### With Multiple Threads

For faster processing with multiple threads:

```bash
python etymology_generator.py --threads 4
```

### Adjust Batch Size

Control how many words are processed in each batch:

```bash
python etymology_generator.py --batch-size 20
```

### Quick Test Run

To test with a small predefined set of words:

```bash
python test_generator.py
```

## Dataset Size Estimates

Based on initial analysis:

- English words: ~370,000
- French words: ~140,000
- Latin words: ~60,000
- Greek words: ~20,000 (estimated)

Total estimated dataset size: ~290MB
Total estimated processing time: ~4.1 days (at 60 words per minute)

## Generated Data Structure

The script generates JSON files with the following structure:

```json
{
  "word": "example",
  "language": "English",
  "year": 1530,
  "definition": "A representative sample",
  "roots": [
    {
      "word": "exemplum",
      "language": "Latin",
      "definition": "sample, pattern",
      "year": 100,
      "roots": [...]
    }
  ]
}
```

## Logging and State

- Log files are created in `backend_script/etymology_generator.log`
- Generator state is saved in `backend_script/generator_state.json`
- Progress statistics are displayed during execution 