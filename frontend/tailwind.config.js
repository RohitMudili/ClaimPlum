/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src//*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
            50: '#f0f4f8',
            100: '#d9e6f2',
            200: '#b3cde0',
            300: '#7fa9cb',
            400: '#5489b8',
            500: '#4a7ba7',
            600: '#3d6690',
            700: '#335578',
            800: '#2a4560',
            900: '#1f3449',
        },
        plum: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
        },
      },
    },
  },
  plugins: [],
}