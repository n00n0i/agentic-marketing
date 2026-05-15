import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic Marketing Platform",
  description: "LLM-driven full-funnel marketing content pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 antialiased">
        {/* Top nav */}
        <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-900/80 backdrop-blur">
          <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
            <Link href="/" className="text-white font-semibold hover:text-blue-400 transition">
              🚀 Agentic Marketing
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-400 hover:text-white text-sm transition">
                Pipeline
              </Link>
              <Link href="/analytics" className="text-gray-400 hover:text-white text-sm transition">
                Analytics
              </Link>
              <Link
                href="/settings"
                className="text-gray-400 hover:text-white text-sm transition flex items-center gap-1"
              >
                ⚙️ Settings
              </Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}