import type { Metadata } from "next";
// import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

// const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Red Team Recon Toolkit",
  description: "Automated OSINT & Reconnaissance Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`min-h-screen bg-background antialiased font-sans`}>
        <Navbar />
        <main className="container mx-auto max-w-screen-2xl pt-16 px-4">
          {children}
        </main>
      </body>
    </html>
  );
}
