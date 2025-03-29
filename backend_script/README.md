# Etymology Dataset Generator

A tool for generating structured etymology data for visualization and analysis.

## Features
- Automated extraction of etymology information from multiple sources
- Support for multiple languages including English, French, German, Latin, and Greek
- Geographic mapping capabilities for visualizing word origins
- Integration with multiple authoritative etymology databases
- Quality scoring for generated etymology data
- Supplementary data system for high-quality verified etymologies
- Customizable output formats (JSON, CSV)
- Test framework to evaluate data quality

## Usage

```bash
python etymology_generator.py [options]
```

### Options

- `--max-words NUM`: Limit processing to NUM words per language
- `--languages LANG1,LANG2,...`: Specify languages to process (default: "English,French,German")
- `--test-mode`: Run in test mode with limited words
- `--sources SOURCE1,SOURCE2,...`: Specify data sources to use (default: "wiktionary,etymonline")
- `--geo-data`: Enable geographical data collection
- `--geo-mapping FILE`: Path to custom geographical mapping file
- `--oed-api-key KEY`: API key for Oxford English Dictionary (if using OED source)

## Etymology Data Sources

The generator can integrate with multiple data sources for etymology information:

### Premium/Academic Resources
- **Oxford English Dictionary (OED) API**: Access to the OED's comprehensive dataset of English language etymology (requires API key)
- **Tower of Babel (Starling) Database**: Etymological database for reconstructing proto-languages
- **Pokorny's Indo-European Etymological Dictionary**: Comprehensive dictionary for Indo-European etymology

### Free/Open Resources
- **Wiktionary**: Multilingual dictionary with etymological information
- **Etymonline**: Online etymology dictionary focused on English word origins
- **Etymological Wordnet**: Database of etymological relations between words
- **University of Texas Indo-European Lexicon**: Resource for Indo-European etymology
- **EtymoloGeek/CoolJugator**: Etymology data from multiple sources with visual representation

## Generated Data Structure

The generator produces JSON files with the following structure:

```json
{
  "word": "example",
  "language": "English",
  "year": 1550,
  "definition": "A representative form or pattern",
  "roots": [
    {
      "word": "exemplum",
      "language": "Latin",
      "definition": "A sample",
      "year": 100,
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
  "sources": ["wiktionary", "oed"]
}
```

## Geographical Features

When enabled with the `--geo-data` flag, the generator will attempt to add geographical origin information to words and their roots.

### Geographical Data Structure
- `lat`: Latitude of the historical center for the language
- `lng`: Longitude of the historical center for the language
- `location`: Human-readable description of the location
- `confidence`: Score from 0-1 indicating confidence in the geographical data

### Custom Mapping Files
You can provide a custom geographical mapping file with the `--geo-mapping` option. This file should be a JSON file mapping language names to geographical coordinates and time periods.

## Supplementary Data

The system includes a supplementary data mechanism for high-quality etymology information. This data takes precedence over other sources and ensures consistent, accurate results for common words.

## Language Support

The generator supports multiple languages, with varying levels of data quality:
- **High Support**: English, Latin, Ancient Greek, French
- **Medium Support**: German, Spanish, Italian, Old English, Middle English, Proto-Germanic
- **Basic Support**: Russian, Portuguese, Sanskrit, Arabic, Proto-Indo-European

The generator can be extended to support additional languages by adding appropriate language mappings and data sources.

## Data Quality

The generator includes a data quality evaluation framework that scores etymology data based on:
- Presence of roots
- Accuracy of language identification
- Presence of sensible definitions
- Year accuracy
- Overall coverage

Quality scores range from 0-100, with the following ratings:
- 80-100: EXCELLENT
- 60-80: GOOD
- 40-60: FAIR
- 20-40: POOR
- 0-20: VERY POOR

## Testing

Run the test script to evaluate the quality of generated etymology data:

```bash
python test_generator.py
```

This will process a sample of words from different languages and output quality metrics.

## Requirements
- Python 3.7 or higher
- Required Python packages are listed in requirements.txt 