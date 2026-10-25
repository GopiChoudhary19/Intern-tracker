import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        mist: "var(--mist)",
        mint: "var(--mint)",
        teal: "var(--teal)",
        coral: "var(--coral)",
        slate: "var(--slate)",
        "surface-strong": "var(--surface-strong)"
      },
      fontFamily: {
        sans: ["Poppins", "ui-sans-serif", "system-ui"]
      },
      boxShadow: {
        glow: "0 20px 60px rgba(29, 127, 116, 0.18)"
      }
    }
  },
  plugins: []
};

export default config;
