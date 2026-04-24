import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          teal: "#0A9396",
          navy: "#1D3557",
          green: "#2D6A4F",
          yellow: "#E9C46A",
          orange: "#E76F51",
        },
        surface: {
          light: "#F8F9FA",
          dark: "#0D1117",
          card: "#161B22",
        },
      },
    },
  },
  plugins: [],
};
export default config;