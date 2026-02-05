/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3f51b5',
          100: '#e0e7ff',
          500: '#3f51b5',
          600: '#303f9f',
        },
        secondary: {
          DEFAULT: '#f50057',
          100: '#fce4ec',
          500: '#f50057',
        },
        background: {
          DEFAULT: '#f7fafc',
          100: '#f5f5f5',
          200: '#e2e8f0',
        },
        surface: {
          DEFAULT: '#ffffff',
          100: '#f8fafc',
          200: '#f1f5f9',
          300: '#e2e8f0',
        },
        textPrimary: '#2d3748',
        textSecondary: '#4a5568',
        textMuted: '#718096',
        textLight: '#a0aec0',
        border: {
          DEFAULT: '#e2e8f0',
          light: '#f0f4f8',
        },
        success: '#4caf50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196f3',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        'xxl': '48px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '16px',
        'round': '50%',
      },
      boxShadow: {
        'sm': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
        'md': '0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)',
        'lg': '0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23)',
      },
      screens: {
        'sm': '576px',
        'md': '768px',
        'lg': '992px',
        'xl': '1200px',
      },
      transitionDuration: {
        'fast': '200ms',
        'normal': '300ms',
        'slow': '500ms',
      },
      fontFamily: {
        'sans': ['Noto Sans KR', 'sans-serif'],
      },
    },
  },
  plugins: [],
  darkMode: 'false',
} 
