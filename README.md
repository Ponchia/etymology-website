# Etymology Website

A modern, sleek etymology website that allows users to input a word and view its etymology chain with a timeline of when each word originated.

## Live Demo

Visit the live site: [Etymology Explorer](https://ponchia.github.io/etymology-website/)

## Overview

- Clean, minimal interface with a centered search input
- Animated transition from search to etymology display
- Visual representation of word origins as connected cards
- Timeline showing when each word in the etymology chain came into use
- Git-based data storage for easy contribution and maintenance
- 100% free hosting on GitHub Pages with data fetched from GitHub repository

## Features

- **Word Search**: Input any word to discover its etymology chain
- **Visual Etymology**: See each word in the chain displayed as a connected card, color-coded by language
- **Timeline Visualization**: View when each word in the chain originated
- **Git as a Database**: All etymology data is stored as JSON files in the GitHub repository
- **GitHub API Integration**: Data is fetched directly from the repository at runtime
- **Responsive Design**: Works well on both desktop and mobile devices
- **Smooth Animations**: Transitions and animations powered by Framer Motion

## How It Works

1. When you search for a word, the app attempts to find it in the repository's data directory
2. The data is fetched using GitHub's raw content URLs for optimal performance
3. The etymology chain is parsed and displayed as connected cards
4. The timeline is generated based on the years each word originated
5. All processing happens client-side with a static site hosted on GitHub Pages

## Technical Architecture

- **Static Site**: Built with Next.js and exported as static HTML/CSS/JS
- **GitHub as Database**: Etymology data stored as JSON files in the repository
- **Client-side Fetching**: Data fetched from GitHub at runtime
- **Serverless Architecture**: No need for a traditional backend

## Data Structure

Etymology data is stored in JSON files with the following structure:

```json
{
  "word": "etymology",
  "language": "English",
  "year": 1398,
  "definition": "the study of the origin and history of words",
  "etymology": [
    {
      "word": "etymologia",
      "language": "Latin",
      "year": 1350
    }
  ],
  "roots": [
    {
      "word": "etymologia",
      "language": "Latin",
      "definition": "origin of words",
      "year": 1350,
      "roots": [
        {
          "word": "etymon",
          "language": "Greek",
          "definition": "true sense",
          "year": null,
          "roots": [...]
        },
        {
          "word": "logia",
          "language": "Greek",
          "definition": "study of",
          "year": null,
          "roots": [...]
        }
      ]
    }
  ]
}
```

## Getting Started

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Ponchia/etymology-website.git
   cd etymology-website
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Adding New Words

1. Create a JSON file in the appropriate language directory:
   ```
   data/words/[Language]/[first-letter]/[word].json
   ```

2. Follow the data structure format shown above
3. Commit and push to the repository

### Deployment

The website is automatically deployed to GitHub Pages using GitHub Actions:

1. Any push to the main branch triggers the deployment workflow
2. The workflow builds the Next.js site as a static export
3. The built files are pushed to the gh-pages branch
4. GitHub Pages serves the content from the gh-pages branch

## Technical Stack

### Core Technologies
- **Next.js v15+**: Using the App Router for modern React architecture
- **React v19+**: For component-based UI
- **TypeScript**: For type safety and better developer experience
- **Framer Motion**: For fluid animations and transitions
- **Tailwind CSS**: For utility-first styling
- **GitHub API**: For data fetching from the repository

### Development Tools
- **ESLint & TypeScript**: For code quality
- **GitHub Actions**: For CI/CD pipeline

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

---

Created with ❤️ by [Ponchia](https://github.com/Ponchia) 