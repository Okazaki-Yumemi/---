/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 38px rgba(79, 209, 255, 0.24)",
        violet: "0 0 34px rgba(139, 92, 246, 0.24)",
      },
    },
  },
  plugins: [],
};
