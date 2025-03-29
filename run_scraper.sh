#!/bin/bash
# Etymology Scraper - Runner Script
# This script provides an easy way to run the various etymology tools using command-line flags

cd "$(dirname "$0")"

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}    ETYMOLOGY SCRAPER SYSTEM     ${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo ""
}

# Print help message
print_help() {
    echo "Usage: ./run_scraper.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  demo                   Run a quick demonstration of the system"
    echo "  create-dict            Create a word list for testing"
    echo "  generate               Process words and generate etymology data"
    echo "  test                   Run a simplified etymology test"
    echo "  help                   Show this help message"
    echo ""
    echo "Options for create-dict:"
    echo "  --output FILE          Output file name (default: dictionary.txt)"
    echo "  --words NUM            Number of words to include (default: 20)"
    echo "  --random               Use random selection (default: true)"
    echo "  --no-random            Disable random selection"
    echo "  --full                 Use full dictionary (default: false)"
    echo "  --no-full              Don't use full dictionary"
    echo ""
    echo "Options for generate:"
    echo "  --wordlist FILE        Word list file (default: data/words/English/dictionary.txt)"
    echo "  --processes NUM        Number of processes to use (default: 1)"
    echo "  --sample               Use sample data for known words (default: false)"
    echo "  --no-sample            Don't use sample data for known words"
    echo ""
    echo "Examples:"
    echo "  ./run_scraper.sh demo"
    echo "  ./run_scraper.sh create-dict --output custom.txt --words 50 --random"
    echo "  ./run_scraper.sh generate --wordlist my_words.txt --processes 4"
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 to use this system.${NC}"
        exit 1
    fi

    # Check for required packages
    if ! python3 -c "import requests, bs4" &> /dev/null; then
        echo -e "${YELLOW}Installing required packages...${NC}"
        pip3 install -r backend_script/requirements.txt
    fi
}

# Function to run the demo
run_demo() {
    echo -e "\n${BLUE}Running Etymology Demo...${NC}\n"
    cd backend_script
    python3 demo.py
    cd ..
    echo -e "\n${GREEN}Demo completed.${NC}"
}

# Function to create a dictionary
create_dictionary() {
    local output_file="dictionary.txt"
    local num_words=20
    local random_flag="--random"
    local full_flag=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --output)
                output_file="$2"
                shift 2
                ;;
            --words)
                num_words="$2"
                shift 2
                ;;
            --random)
                random_flag="--random"
                shift
                ;;
            --no-random)
                random_flag=""
                shift
                ;;
            --full)
                full_flag="--full"
                shift
                ;;
            --no-full)
                full_flag=""
                shift
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "\n${BLUE}Creating Dictionary...${NC}"
    echo -e "${BLUE}Output file: ${output_file}${NC}"
    echo -e "${BLUE}Number of words: ${num_words}${NC}"
    echo -e "${BLUE}Random selection: $([ -n "$random_flag" ] && echo "Yes" || echo "No")${NC}"
    echo -e "${BLUE}Full dictionary: $([ -n "$full_flag" ] && echo "Yes" || echo "No")${NC}"
    
    # Create output directory if it doesn't exist
    mkdir -p data/words/English
    
    # Run the command
    cd backend_script
    python3 create_dictionary.py --output "../data/words/English/$output_file" --words "$num_words" $random_flag $full_flag
    cd ..
    
    echo -e "\n${GREEN}Dictionary created at data/words/English/$output_file${NC}"
}

# Function to generate etymology data
generate_etymology() {
    local word_list="data/words/English/dictionary.txt"
    local num_processes=1
    local sample_flag=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --wordlist)
                word_list="$2"
                shift 2
                ;;
            --processes)
                num_processes="$2"
                shift 2
                ;;
            --sample)
                sample_flag="--use-sample"
                shift
                ;;
            --no-sample)
                sample_flag=""
                shift
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "\n${BLUE}Generating Etymology Data...${NC}"
    echo -e "${BLUE}Word list: ${word_list}${NC}"
    echo -e "${BLUE}Processes: ${num_processes}${NC}"
    echo -e "${BLUE}Use sample data: $([ -n "$sample_flag" ] && echo "Yes" || echo "No")${NC}"
    
    # Run the command
    cd backend_script
    python3 generate_etymology.py --word-list "../$word_list" --processes "$num_processes" --output-dir "../data/words/English" --store-by-first-letter $sample_flag
    cd ..
    
    echo -e "\n${GREEN}Etymology generation completed. Files stored in data/words/English/[first_letter]/ folders${NC}"
}

# Function to run a simple test
run_simple_test() {
    echo -e "\n${BLUE}Running Simple Etymology Test...${NC}\n"
    cd backend_script
    python3 test_etymology_simple.py
    cd ..
    echo -e "\n${GREEN}Test completed.${NC}"
}

# Main function
main() {
    print_header
    check_python
    
    # No arguments provided
    if [ $# -eq 0 ]; then
        print_help
        exit 0
    fi
    
    command="$1"
    shift
    
    case "$command" in
        demo)
            run_demo
            ;;
        create-dict)
            create_dictionary "$@"
            ;;
        generate)
            generate_etymology "$@"
            ;;
        test)
            run_simple_test
            ;;
        help)
            print_help
            ;;
        *)
            echo -e "${RED}Error: Unknown command: $command${NC}"
            print_help
            exit 1
            ;;
    esac
}

# Run the main function
main "$@" 