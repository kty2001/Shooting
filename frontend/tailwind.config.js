/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Dark background layers */
        background: {
          DEFAULT: '#080e1a',
          100: '#0b1220',
          200: '#0f1829',
        },

        surface: {
          DEFAULT: '#111d30',
          100: '#162038',
          200: '#1a2744',
          300: '#1e3054',
        },

        /* Company blue palette */
        primary: {
          DEFAULT: '#2563eb',
          100: '#dbeafe',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },

        /* Text */
        textPrimary:   '#f1f5f9',
        textSecondary: '#94a3b8',
        textMuted:     '#64748b',
        textLight:     '#cbd5e1',
        textWhite:     '#ffffff',

        /* Borders */
        border: {
          DEFAULT: '#1e3a5f',
          light:   '#253c6e',
        },

        /* Status */
        success: '#22c55e',
        error:   '#ef4444',
        warning: '#f59e0b',
        info:    '#3b82f6',
      },

      spacing: {
        xs:  '4px',
        sm:  '8px',
        md:  '16px',
        lg:  '24px',
        xl:  '32px',
        xxl: '48px',
      },

      borderRadius: {
        sm:    '4px',
        md:    '8px',
        lg:    '16px',
        round: '50%',
      },

      boxShadow: {
        sm:   '0 1px 3px rgba(0,0,0,0.4)',
        md:   '0 3px 6px rgba(0,0,0,0.5)',
        lg:   '0 10px 20px rgba(0,0,0,0.6)',
        blue: '0 0 12px rgba(37,99,235,0.4)',
      },

      screens: {
        sm: '576px',
        md: '768px',
        lg: '992px',
        xl: '1200px',
      },

      transitionDuration: {
        fast:   '200ms',
        normal: '300ms',
        slow:   '500ms',
      },

      fontFamily: {
        sans: ['Noto Sans KR', 'sans-serif'],
      },
    },
  },
  plugins: [],
  darkMode: false,
}
