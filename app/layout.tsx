import 'reactflow/dist/style.css';
import './globals.css';
import './reactflow-styles.css';
import type { Metadata } from 'next';

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