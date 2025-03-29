#!/usr/bin/env python3
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_data_sources")

class DataSourcesTest:
    def __init__(self):
        self.sources = ["wiktionary", "etymonline", "etymwordnet", "ielex", "starling"]
        self.cache_dir = os.path.join(".", "cache")
        self.data_sources = {}
        
        # Ensure cache directories exist
        os.makedirs(self.cache_dir, exist_ok=True)
        for source in self.sources:
            source_dir = os.path.join(self.cache_dir, source)
            os.makedirs(source_dir, exist_ok=True)
            
    def init_wiktionary_source(self):
        """Initialize the Wiktionary data source."""
        wiktionary_cache = os.path.join(self.cache_dir, "wiktionary")
        wiktionary_index = os.path.join(wiktionary_cache, "index.json")
        
        if not os.path.exists(wiktionary_index):
            logger.info("Creating Wiktionary cache index...")
            with open(wiktionary_index, 'w') as f:
                json.dump({"last_updated": "2023-03-29"}, f)
        
        return {"cache_dir": wiktionary_cache, "index": wiktionary_index}

    def init_etymonline_source(self):
        """Initialize the Etymonline data source."""
        etymonline_cache = os.path.join(self.cache_dir, "etymonline")
        return {"cache_dir": etymonline_cache}

    def init_etymwordnet_source(self):
        """Initialize the etymological wordnet data source."""
        etymwordnet_cache = os.path.join(self.cache_dir, "etymwordnet")
        return {"cache_dir": etymwordnet_cache}

    def init_ielex_source(self):
        """Initialize the University of Texas Indo-European Lexicon source."""
        ielex_cache = os.path.join(self.cache_dir, "ielex")
        return {"cache_dir": ielex_cache, "base_url": "https://lrc.la.utexas.edu/lex/master"}
        
    def init_starling_source(self):
        """Initialize the Tower of Babel (Starling) database source."""
        starling_cache = os.path.join(self.cache_dir, "starling")
        return {"cache_dir": starling_cache, "base_url": "https://starling.rinet.ru/cgi-bin/response.cgi"}
        
    def load_data_sources(self):
        """Load and initialize all data sources."""
        available_sources = {
            "wiktionary": self.init_wiktionary_source,
            "etymonline": self.init_etymonline_source,
            "etymwordnet": self.init_etymwordnet_source,
            "ielex": self.init_ielex_source,
            "starling": self.init_starling_source
        }
        
        # Initialize the data_sources dictionary
        self.data_sources = {}
        
        # Initialize each source
        for source in self.sources:
            if source in available_sources:
                logger.info(f"Initializing data source: {source}")
                try:
                    # Call the initialization function and store its return value
                    source_data = available_sources[source]()
                    # Store the source's data in the data_sources dict
                    self.data_sources[source] = source_data
                    logger.info(f"Successfully initialized {source}")
                except Exception as e:
                    logger.error(f"Error initializing {source}: {str(e)}")
            else:
                logger.warning(f"Unknown data source: {source}")
                
        # Log the initialized sources
        logger.info(f"Initialized {len(self.data_sources)} data sources")
        
    def run_tests(self):
        """Run tests on data sources"""
        logger.info("Starting data sources tests")
        
        # Load data sources
        self.load_data_sources()
        
        # Check if all sources are initialized
        all_initialized = True
        for source in self.sources:
            if source in self.data_sources:
                logger.info(f"✅ {source} is properly initialized")
                # Check if cache directory exists
                cache_dir = self.data_sources[source].get("cache_dir")
                if cache_dir and os.path.exists(cache_dir):
                    logger.info(f"   Cache directory: {cache_dir}")
                else:
                    logger.warning(f"   Cache directory not found for {source}")
                    all_initialized = False
            else:
                logger.error(f"❌ {source} is not initialized")
                all_initialized = False
                
        if all_initialized:
            logger.info("All data sources are properly initialized and ready to use")
        else:
            logger.warning("Some data sources failed to initialize properly")
            
        return all_initialized

if __name__ == "__main__":
    test = DataSourcesTest()
    test.run_tests() 