import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#171717",
        graphite: "#3F4148",
        field: "#F5F6F4",
        line: "#D8DAD4",
        signal: "#0F766E",
        warning: "#B45309",
        danger: "#B91C1C",
        violet: "#5B4DB7"
      },
      fontFamily: {
        sans: ["Inter", "Arial", "sans-serif"],
        mono: ["IBM Plex Mono", "Menlo", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;

