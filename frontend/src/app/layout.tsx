import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { Providers } from "@/components/Providers";

/**
 * Brand typography, loaded & self-hosted by next/font (zero layout shift).
 * - Playfair Display → elegant serif for headings
 * - Inter           → clean sans for body copy
 * Both are exposed as CSS variables consumed by tailwind.config.ts.
 */
const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://savoria.example.com"),
  title: {
    default: "Savoria — Fine Dining Restaurant",
    template: "%s | Savoria",
  },
  description:
    "Savoria serves seasonal, chef-crafted dishes made from the finest local ingredients. Explore our menu and order online.",
  keywords: ["restaurant", "fine dining", "menu", "order food", "Savoria"],
  openGraph: {
    title: "Savoria — Fine Dining Restaurant",
    description:
      "Seasonal, chef-crafted dishes made from the finest local ingredients.",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${playfair.variable} ${inter.variable} h-full scroll-smooth`}
    >
      <body className="flex min-h-full flex-col bg-cream-100 text-espresso-900">
        <Providers>
          {/* Skip link for keyboard & screen-reader users. */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-espresso-900 focus:px-4 focus:py-2 focus:text-cream-50"
          >
            Skip to content
          </a>
          <Navbar />
          <div id="main-content" tabIndex={-1} className="flex-1 outline-none">
            {children}
          </div>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
