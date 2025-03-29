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

## Current Implementation

The project has been implemented with the following features:

1. Homepage with a centered, styled search input
2. Search functionality that fetches word etymology data from a GitHub repository
3. Etymology displayed as connected cards with color-coding by language
4. Timeline component showing when each word in the chain came into use
5. Error handling for non-existent words
6. Responsive design that works on both mobile and desktop

## Data Architecture

This project uses GitHub as both a hosting platform and a data source:

- The web application is hosted on GitHub Pages
- Etymology data is stored as JSON files in the same GitHub repository
- The app fetches data at runtime using the GitHub API
- This approach eliminates the need for a traditional database or backend

In development mode, a sample etymology entry is provided for testing. In production, the application loads data directly from the GitHub repository.

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser

5. To deploy to GitHub Pages:
   - Update the repository settings in `app/services/wordService.ts`
   - Build and deploy using GitHub Actions (see configuration below)

## GitHub Pages Deployment

This project uses GitHub Actions to deploy to GitHub Pages:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: npm run build
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./out
```

## Technical Stack

### Core Technologies
- **Next.js v15+**: Using the App Router
  - File-based routing system
  - Client and Server Components
- **React v19+**: For component-based UI architecture
- **TypeScript**: For type safety and better developer experience

### Styling & Design
- **Tailwind CSS v4+**: For utility-first styling
  - Custom design system with language-specific colors
  - Responsive design elements
- **Framer Motion v12+**: For fluid animations and transitions
  - Animation variants for card appearance
  - Staggered animations for etymology chain
- **Lucide Icons**: For minimal, clean icons

### Data Management
- **JSON Files**: Etymology data stored as structured JSON
- **Custom Data Service**: For fetching and processing etymology data

## Project Structure

```
etymology-website/
├── app/
│   ├── components/
│   │   ├── EtymologyCard.tsx
│   │   ├── EtymologyChain.tsx
│   │   ├── SearchInput.tsx
│   │   └── Timeline.tsx
│   ├── services/
│   │   └── wordService.ts
│   ├── types/
│   │   └── index.ts
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── public/
│   └── data/
│       └── words/
│           └── English/
│               └── e/
│                   └── etymology.json
├── next.config.ts
├── package.json
├── postcss.config.mjs
└── tailwind.config.mjs
```

## Data Format

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
          "roots": [
            {
              "word": "etymos",
              "language": "Greek",
              "definition": "true, real, actual",
              "year": null
            }
          ]
        },
        {
          "word": "logia",
          "language": "Greek",
          "definition": "study of",
          "year": null,
          "roots": [
            {
              "word": "logos",
              "language": "Greek",
              "definition": "word, speech, discourse, reason",
              "year": null
            }
          ]
        }
      ]
    }
  ]
}
```

## Future Enhancements

- Add more words to the etymology database
- Implement GitHub API-based data retrieval for production
- Add ability for users to contribute new words
- Improve mobile responsiveness
- Add dark/light mode toggle
- Add testing with Jest and React Testing Library
- Implement Storybook for component development

## User Experience

1. Homepage displays only a centered, styled search input
2. Upon entering a word, the input transitions to become the last card in the etymology chain
3. Etymology is displayed as connected cards (similar to the example image)
4. A timeline appears on the right showing when each word in the chain came into use

## Technical Specification

### Frontend Stack

- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion for smooth transitions
- **Hosting**: GitHub Pages (100% free)

## Technical Stack Details

### Core Technologies
- **Next.js v14+**: Utilizing the App Router for better performance and SEO
  - File-based routing system
  - Server Components for improved initial load time
  - Built-in API routes for potential future expansion
  - Static Export option for GitHub Pages compatibility
- **React v18+**: For component-based UI architecture
- **TypeScript**: For type safety and better developer experience

### Styling & Design
- **Tailwind CSS v3+**: For utility-first styling
  - Custom design system configuration in `tailwind.config.js`
  - `@tailwindcss/typography` plugin for rich text styling
  - `@tailwindcss/forms` plugin for input element styling
- **Framer Motion v10+**: For fluid animations and transitions
  - Animation variants for consistent motion design
  - Layout animations for card transitions
- **Lucide Icons**: Modern icon library with consistent styling
- **Google Fonts**: Inter and Playfair Display

### Data Management
- **SWR**: For data fetching, caching, and revalidation
- **raw-loader**: For importing JSON files directly in development
- **Octokit/REST**: GitHub API client for production data fetching from repository (with support for unauthenticated requests)
- **simple-git-hooks**: For CI validation of data files
- **zod**: For JSON schema validation

### Developer Tools
- **ESLint**: Configured with Next.js defaults plus custom rules
- **Prettier**: For consistent code formatting
- **Husky**: For pre-commit hooks
- **Jest** & **React Testing Library**: For unit and component testing
- **Storybook**: For component development and documentation

### Build & Deployment
- **GitHub Pages**: For free static site hosting
- **GitHub Actions**: For CI/CD pipeline and data validation
- **Turbopack**: For faster development experience

## Free Hosting Strategy

This project is designed to be completely free to host and maintain:

1. **GitHub Pages for Hosting**:
   - Uses Next.js static export (`next export`) to generate static HTML/CSS/JS
   - Set up GitHub Actions workflow to automatically build and deploy to GitHub Pages branch
   - Configure with custom domain (optional) or use the free `username.github.io/repo-name` domain

2. **GitHub Repository as Database**:
   - Store all etymology data as JSON files directly in the repository
   - No need for a traditional backend or database service
   - All data changes are version-controlled through Git history

3. **GitHub API for Data Retrieval**:
   - Use GitHub's REST API to fetch JSON files at runtime
   - Implement client-side caching to minimize API calls
   - Stay within GitHub's free tier rate limits (5,000 requests/hour for authenticated requests with a GitHub App, 60 requests/hour for unauthenticated requests)

4. **Edge Caching Strategy**:
   - Store frequently accessed words in localStorage/sessionStorage
   - Implement a service worker for offline capability and caching
   - Use CDN caching headers for optimal performance

### Data Storage

- **Repository Structure**:
  ```
  /data
    /words
      /[language]
        /[first-letter]
          word1.json
          word2.json
  ```
- **Word JSON Format**:
  ```json
  {
    "word": "pornography",
    "language": "English",
    "year": 1842,
    "definition": "ancient obscene painting, especially in temples of Bacchus",
    "etymology": [
      {
        "word": "pornographie",
        "language": "French",
        "year": 1830
      }
    ],
    "roots": [
      {
        "word": "pornographos",
        "language": "Greek",
        "definition": "depicting prostitutes",
        "year": null,
        "roots": [
          {
            "word": "porne",
            "language": "Greek",
            "definition": "prostitute",
            "roots": [
              {
                "word": "pernanai",
                "language": "Greek",
                "definition": "to sell"
              }
            ]
          },
          {
            "word": "graphein",
            "language": "Greek",
            "definition": "to write"
          }
        ]
      }
    ]
  }
  ```

### Data Management Workflow

1. Etymology data is stored in Git repository as JSON files
2. Contributors can add new words by creating JSON files and submitting PRs
3. CI/CD pipeline validates JSON structure
4. Website builds from the data in the repository

## Expanding the Word Database

The etymological data can be expanded and maintained in several automated and semi-automated ways:

### 1. LLM-Powered Etymology Generation

- **Automated Research Scripts**:
  - Python scripts that use LLMs (OpenAI API, Anthropic Claude, etc.) to research word etymologies
  - Scripts can generate properly formatted JSON files from LLM output
  - Setup GitHub Actions workflow to periodically run these scripts and automatically open PRs with new words

- **Etymological Verification Workflow**:
  - Generate initial etymologies with LLMs
  - Human reviewer validates accuracy
  - Approved words get merged into the main dataset

### 2. Crowdsourced Contributions

- **Contributor Tools**:
  - Web-based form for adding new words directly from the website
  - Form submits data as a PR to the repository
  - Automated validation ensures correct JSON structure

- **Review Process**:
  - GitHub Actions workflow validates new PRs for format consistency
  - Community review for accuracy
  - Maintainer approval and merge

### 3. Data Scraping and Integration

- **Ethymology Dictionary APIs**:
  - Scripts to fetch data from open etymological sources
  - Convert and normalize to our JSON format
  - Add source attribution

- **Academic Dataset Integration**:
  - Scripts to convert academic word origin datasets to our format
  - Focus on open-licensed data sources

### 4. Automated Maintenance

- **Consistency Checking**:
  - Regular scripts to check for and fix inconsistencies in the dataset
  - Merge duplicate records
  - Standardize language naming and formatting

- **Link Verification**:
  - Verify that all etymological links are valid
  - Fix broken chains in the etymology tree

The combination of AI-assisted generation, crowdsourcing, and automated maintenance allows for sustainable growth of the etymology database without requiring significant ongoing cost or manual effort.

## Implementation Plan

### Phase 1: Basic Structure
- Set up Next.js project with Tailwind CSS
- Create homepage with styled search input
- Implement basic word lookup from JSON files

### Phase 2: Visualization
- Build etymology card component system
- Implement animation transitions
- Create timeline visualization component

### Phase 3: Data Management
- Set up Git repository structure for etymology data
- Create documentation for contributors
- Implement data validation scripts

## Component Structure

- **SearchInput**: Main entry point, styled input that transforms
- **EtymologyChain**: Container for etymology cards
- **EtymologyCard**: Individual word card with styling based on language
- **Timeline**: Vertical timeline showing years of word origins
- **ConnectionLine**: SVG component for arrows between cards

## Design Notes

- Color scheme based on language origins (Greek: light red, French: blue, etc.)
- Typography: Primary font - Inter, Secondary font - Playfair Display for historical feel
- Responsive design that works on mobile and desktop
- Dark/Light mode toggle
- Subtle animations for transitions between states

## Development Setup

1. Initialize the project:
   ```bash
   npx create-next-app@latest etymology-website --typescript --tailwind --app --eslint --src-dir --import-alias "@/*"
   cd etymology-website
   ```

2. Install additional dependencies:
   ```bash
   npm install framer-motion swr octokit zod lucide-react
   npm install -D @tailwindcss/typography @tailwindcss/forms husky simple-git-hooks jest @testing-library/react @storybook/react
   ```

3. Run development server: `npm run dev`
4. Add word data to `/data/words/` following the JSON format
5. Build for production: `npm run build && npm run export`
6. Deploy to GitHub Pages using GitHub Actions

## Git-based Backend Strategy

- Use GitHub API to read JSON files directly from repository
- Store word data in structured folders by language and first letter
- Use GitHub Actions to validate data format on PR
- Implement caching strategy for frequently accessed words

## Package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.16.4",
    "swr": "^2.2.4",
    "octokit": "^3.1.1",
    "zod": "^3.22.4",
    "lucide-react": "^0.290.0"
  },
  "devDependencies": {
    "@types/node": "^20.8.9",
    "@types/react": "^18.2.33",
    "typescript": "^5.2.2",
    "tailwindcss": "^3.3.5",
    "@tailwindcss/typography": "^0.5.10",
    "@tailwindcss/forms": "^0.5.6",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.52.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.3",
    "husky": "^8.0.3",
    "simple-git-hooks": "^2.9.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.0.0",
    "@storybook/react": "^7.5.1"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "export": "next export",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

This approach leverages Git as a database while keeping the frontend static and performant. 