import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true, // Required for static export
  },
  // GitHub Pages deploys to a subdirectory by default (repo name)
  // Set this to match your repository name, or use "" for a custom domain
  basePath: process.env.NODE_ENV === 'production' ? '/etymology-website' : '',
};

export default nextConfig;
