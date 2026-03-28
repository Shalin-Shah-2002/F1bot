import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: "#124E78",
          cream: "#F0F0C9",
          gold: "#F2BB05",
          orange: "#D74E09",
          burgundy: "#6E0E0A"
        }
      }
    }
  },
  plugins: []
};

export default config;
