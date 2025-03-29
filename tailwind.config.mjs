import typography from '@tailwindcss/typography';
import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
      colors: {
        'etymology-blue': '#3B82F6',
        'etymology-red': '#EF4444',
        'etymology-green': '#10B981',
        'etymology-yellow': '#F59E0B',
        'etymology-purple': '#8B5CF6',
      },
    },
  },
  plugins: [
    typography,
    forms,
  ],
}; 