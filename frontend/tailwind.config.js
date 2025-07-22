/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // HiddenThread custom colors
        'ht-bg': '#0f0f1a',
        'ht-text': '#e0e0ff',
        'ht-purple': '#7f5af0',
        'ht-blue': '#1f1f3a',
        'ht-card': '#1a1a2e',
        'ht-border': '#444466',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow': '0 0 20px -5px rgba(127, 90, 240, 0.3)',
        'glow-lg': '0 0 40px -5px rgba(127, 90, 240, 0.4)',
      },
    },
  },
  plugins: [],
};