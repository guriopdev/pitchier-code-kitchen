import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ExtensionAttributeCleaner } from "@/components/ExtensionAttributeCleaner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Startup Pitch Builder — Institutional 10-Slide Engine",
  description:
    "Open-source platform to synthesize founder notes into strict 10-slide decks with venture partner stress-testing and native export.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      suppressHydrationWarning
    >
      <body
        className="min-h-screen bg-[var(--color-paper)] text-[var(--color-ink)] font-sans selection:bg-[#dfd8ca] selection:text-[#1c1917]"
        suppressHydrationWarning
      >
        <ExtensionAttributeCleaner />
        {children}
      </body>
    </html>
  );
}
