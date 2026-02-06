/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Core grayscale palette */
        gray: {
          50:  '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },

        /* Semantic colors (mapped to grayscale) */
        primary: {
          DEFAULT: '#262626',   // gray-800
          100: '#f5f5f5',
          500: '#404040',
          600: '#262626',
        },

        secondary: {
          DEFAULT: '#525252',   // gray-600
          100: '#e5e5e5',
          500: '#525252',
        },

        background: {
          DEFAULT: '#fafafa',   // gray-50
          100: '#f5f5f5',
          200: '#e5e5e5',
        },

        surface: {
          DEFAULT: '#ffffff',
          100: '#fafafa',
          200: '#f5f5f5',
          300: '#e5e5e5',
        },

        /* Text */
        textPrimary: '#171717',    // gray-900
        textSecondary: '#404040',  // gray-700
        textMuted: '#737373',      // gray-500
        textLight: '#a3a3a3',      // gray-400

        /* Borders */
        border: {
          DEFAULT: '#e5e5e5',
          light: '#f5f5f5',
        },

        /* Status (still semantic, visually grayscale) */
        success: '#404040',
        error: '#262626',
        warning: '#525252',
        info: '#737373',
      },

      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        xxl: '48px',
      },

      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '16px',
        round: '50%',
      },

      boxShadow: {
        sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
        md: '0 3px 6px rgba(0, 0, 0, 0.16)',
        lg: '0 10px 20px rgba(0, 0, 0, 0.19)',
      },

      screens: {
        sm: '576px',
        md: '768px',
        lg: '992px',
        xl: '1200px',
      },

      transitionDuration: {
        fast: '200ms',
        normal: '300ms',
        slow: '500ms',
      },

      fontFamily: {
        sans: ['Noto Sans KR', 'sans-serif'],
      },
    },
  },
  plugins: [],
  darkMode: false,
}
