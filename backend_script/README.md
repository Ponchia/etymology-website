# Etymology Dataset Generator

A sophisticated tool to generate high-quality etymological data for visualization and analysis.

## Features

- Generate etymological data for words from multiple languages
- Trace word origins through various historical languages
- Include geographical origin information for mapping visualization
- Integrate with multiple free etymology data sources
- Support for multiple languages (English, French, German, Latin, Greek, etc.)
- Quality scoring system for generated data
- Caching system for efficient processing

## Usage

```
python etymology_generator.py --max-words 100 --sources wiktionary,etymonline,etymwordnet,starling,ielex
```

### Options

- `--max-words`: Maximum number of words to process
- `--languages`: Comma-separated list of languages to include
- `--sources`: Comma-separated list of etymology data sources to use
- `--geo-data`: Enable geographical data collection
- `--geo-mapping`: Path to custom geographical mapping file
- `--test`: Run in test mode on a predefined set of words

## Etymology Data Sources

The generator can utilize multiple free etymology data sources:

### Free/Open Resources

- **Wiktionary**: Community-driven multilingual dictionary with etymological information
- **Etymonline**: Online etymology dictionary focused on English words
- **Etymological Wordnet**: Network of etymological and derivational relations extracted from Wiktionary
- **University of Texas Indo-European Lexicon (IELEX)**: Collection of Indo-European roots and cognates
- **Tower of Babel/Starling Database**: Comparative linguistics database for proto-language reconstruction

## Data Structure

The generated data is stored as JSON files with the following structure:

```json
{
  "word": "example",
  "language": "English",
  "year": 1530,
  "definition": "A representative form or pattern",
  "roots": [
    {
      "word": "exemplum",
      "language": "Latin",
      "year": 100,
      "definition": "sample",
      "geo_origin": {
        "lat": 41.9028,
        "lng": 12.4964,
        "location": "Rome, Italy",
        "confidence": 0.8
      }
    }
  ],
  "geo_origin": {
    "lat": 51.5074,
    "lng": -0.1278,
    "location": "London, England",
    "confidence": 0.7
  },
  "quality_score": 75
}
```

## Geographical Features

When enabled, the generator will include geographical origin information for words and their roots. This data can be used to create visualizations showing how words moved across regions and cultures.

### Enabling Geographic Data

Use the `--geo-data` flag to enable geographical data collection:

```
python etymology_generator.py --max-words 100 --geo-data
```

### Custom Mapping

You can provide a custom geographical mapping file using the `--geo-mapping` option:

```
python etymology_generator.py --max-words 100 --geo-data --geo-mapping custom_mapping.json
```

## Language Support

The generator supports multiple languages including:

- English
- French
- German
- Latin
- Greek (Ancient and Modern)
- Spanish
- Italian
- Russian
- And more...

## Data Quality

The quality of the generated etymology data is evaluated based on several metrics:

- Presence of year information
- Quality of root words
- Presence of sensible definitions
- Alignment with expected language origins
- Geographical data accuracy

Quality scores range from 0 to 100, with the following categories:

- 0-25: POOR
- 26-50: FAIR
- 51-75: GOOD
- 76-100: EXCELLENT

## Performance

The generator uses a caching system to avoid redundant network requests and improve performance. For large datasets, the process can be time-consuming due to rate limiting on web scraping. The estimation for processing time is:

- Small dataset (100 words): ~5 minutes
- Medium dataset (1,000 words): ~1 hour
- Large dataset (10,000+ words): ~10+ hours

## Dependencies

- Python 3.6+
- requests
- beautifulsoup4
- tqdm

## Installation

```
pip install -r requirements.txt
``` 