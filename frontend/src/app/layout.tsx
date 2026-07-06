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
          <Navbar />
          <div className="flex-1">{children}</div>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
