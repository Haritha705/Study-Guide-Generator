import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "StudyPack AI — Intelligent Study Guide & Adaptive Assessment System",
  description:
    "Transform lecture notes, syllabi, and PDFs into structured study packs with executive summaries, progressive difficulty MCQs (Easy, Medium, Hard), 3D flashcards, comprehensive glossaries, and context-aware AI tutoring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      appearance={{
        theme: dark,
        variables: {
          colorPrimary: "#6366f1",
          colorBackground: "#0d0d12",
        },
      }}
    >
      <html lang="en" className="dark">
        <body
          className={`${inter.variable} font-sans antialiased bg-[#09090b] text-neutral-100 min-h-screen selection:bg-indigo-600 selection:text-white`}
        >
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
