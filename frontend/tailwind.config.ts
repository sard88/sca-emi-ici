import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        guinda: {
          DEFAULT: "#611232",
          accent: "#9F2241",
        },
        militar: {
          DEFAULT: "#235B4E",
          olive: "#3A4A32",
        },
        oro: {
          DEFAULT: "#D4AF37",
          muted: "#BC955C",
        },
        marfil: "#F8F4EA",
        carbon: "#1F2937",
      },
      boxShadow: {
        institutional: "0 24px 60px rgba(31, 41, 55, 0.14)",
      },
    },
  },
  plugins: [],
};

export default config;
