import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ATLAS - AI-Powered Business Intelligence',
  description: 'Transform global information streams into actionable business intelligence using multi-source data processing, causal reasoning, and explainable AI.',
  keywords: ['business intelligence', 'AI', 'machine learning', 'market intelligence', 'opportunity detection'],
  authors: [{ name: 'ATLAS Team' }],
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
