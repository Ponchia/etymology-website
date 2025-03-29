import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Etymology Explorer',
  description: 'Discover the origins of words through their etymology chains',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
} 