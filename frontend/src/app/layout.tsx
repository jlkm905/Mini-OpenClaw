import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'mini OpenClaw',
  description: 'Local-first personal AI assistant',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden bg-[#fafafa]">{children}</body>
    </html>
  );
}
