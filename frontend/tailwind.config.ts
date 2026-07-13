import type { Config } from "tailwindcss";

/**
 * Tailwind theme for "Savoria" — a warm, luxury fine-dining aesthetic.
 *
 * Palette:
 *   - cream     → soft warm off-white backgrounds
 *   - espresso  → deep near-black browns for text & dark sections
 *   - gold      → the signature brand accent (buttons, highlights)
 */
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        cream: {
          50: "#fdfcf9",
          100: "#faf6ef",
          200: "#f3ebdb",
          300: "#e9dcc2",
        },
        espresso: {
          50: "#f6f4f2",
          100: "#e3ddd7",
          400: "#8a7b6d",
          600: "#4a3f36",
          800: "#2b241f",
          900: "#1c1713",
        },
        gold: {
          50: "#fbf7ee",
          100: "#f5ebd2",
          200: "#e9d3a0",
          300: "#dcb96c",
          400: "#cfa244",
          500: "#b8862f", // primary brand accent
          600: "#9a6d25",
          700: "#7a5420",
        },
      },
      fontFamily: {
        // Wired to next/font CSS variables set in layout.tsx.
        serif: ["var(--font-playfair)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px -12px rgba(28, 23, 19, 0.18)",
        "card-hover": "0 20px 40px -14px rgba(28, 23, 19, 0.28)",
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.94)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "0.6" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.6s ease-out both",
        "fade-in": "fade-in 0.8s ease-out both",
        "scale-in": "scale-in 0.5s ease-out both",
        float: "float 6s ease-in-out infinite",
        "pulse-glow": "pulse-glow 5s ease-in-out infinite",
        shimmer: "shimmer 1.6s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
