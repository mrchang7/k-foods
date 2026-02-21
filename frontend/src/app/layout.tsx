import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Korean Food Encyclopedia | K-Food",
  description: "Netflix-style curation of the best Korean Food recipes from YouTube.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.className} antialiased min-h-screen bg-[#141414] text-white`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
