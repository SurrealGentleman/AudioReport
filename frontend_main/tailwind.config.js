/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{jsx,js}"],
  theme: {
    extend: {
      colors: {
        "brand-blue": "#373B72",
        "brand-grey": "#EFEEEE",
        "brand-purple": "#B9BCDC",
      },
    },
  },
  plugins: [],
};
