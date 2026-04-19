/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        // Editorial display serif with variable axes — used for headings
        display: ['"Instrument Serif"', "Georgia", "serif"],
        // Technical sans — used for UI + body text
        sans: ['"IBM Plex Sans"', "system-ui", "sans-serif"],
        // Monospace for numerical readouts + clause IDs
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      colors: {
        // Parchment background — warmer than white, intentionally off
        parchment: {
          50: "#fdfbf7",
          100: "#fbf9f4",
          200: "#f2ede1",
          300: "#e8dfcc",
        },
        // Deep legal ink
        ink: {
          900: "#0a1e3a",
          800: "#14283f",
          700: "#28384f",
          600: "#43516a",
          500: "#6b7690",
        },
        // Cognac / amber — the single warm accent in the whole design
        cognac: {
          50: "#faf1e8",
          400: "#d17f47",
          500: "#b8562c",
          600: "#8e3f1f",
          700: "#6e2f17",
        },
        // Five-band level palette — editorial, not stock red-to-green
        level: {
          "highly-atypical": "#8b2f1f",
          atypical: "#b8562c",
          mixed: "#8a7a40",
          standard: "#4a6b4f",
          "highly-standard": "#2d4a3e",
        },
      },
      letterSpacing: {
        tightest: "-0.04em",
        "wide-cap": "0.14em",
      },
      boxShadow: {
        card: "0 1px 0 rgba(10, 30, 58, 0.08)",
        inset: "inset 0 0 0 1px rgba(10, 30, 58, 0.12)",
      },
    },
  },
  plugins: [],
};
