import type { Metadata } from "next";
import { Inter, Montserrat, JetBrains_Mono } from "next/font/google";
import QueryProvider from "./providers/QueryProvider";
import "./globals.css";

/*
 * FONT STRATEGY (from Design.txt):
 *   - Inter:          Body text — clean, highly legible at small sizes.
 *   - Montserrat:     Headers — bold geometric sans-serif, "command center" feel.
 *   - JetBrains Mono: Spreadsheet cells — monospace for aligned data columns.
 *
 * WHY next/font/google?
 *   Google Fonts are self-hosted at build time (no external requests at runtime).
 *   This gives us zero layout shift and better privacy vs. a <link> tag.
 *
 * ALTERNATIVE: @font-face with local files — full control but requires
 *   managing font files, subsetting, and WOFF2 conversion manually.
 */

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  display: "swap",
  weight: ["600", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SheetAgent — Agentic Spreadsheet Platform",
  description:
    "AI-powered spreadsheet for college-fest organizers. Automate WhatsApp, emails, and data cleaning with intelligent agents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${montserrat.variable} ${jetbrainsMono.variable} antialiased`}
      >
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}

