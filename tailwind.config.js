const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    './src/templates/**/*.html',
    './src/static/src/**/*.js',
    './src/exchange/forms.py',
    './src/orders/forms.py',
    './src/projects/forms.py',
    './src/users/forms.py',
  ],
  theme: {
    container: {
      center: true,
      padding: '1rem',
      screens: {
        '2xl': '1280px',
      },
    },
    extend: {
      fontFamily: {
        sans: ['Montserrat', ...defaultTheme.fontFamily.sans],
        display: ['Raleway', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        'ukraine-blue': '#0057B7',
        'ukraine-yellow': '#FFD700',
        'light-bg': '#F7F7F7',
        'dark-text': '#2C2C2C',
        'accent-gray': '#EAEAEA',
        'pastel-blue': '#A8D8EA',
        'brand-blue': '#0057B7',
        'brand-yellow': '#FFD700',
        'light-gray': '#F5F5F5',
        'dark-gray': '#333333',
        'medium-gray': '#A0A0A0',
        'soft-blue': '#E6F0FF',
        'soft-yellow': '#FFF8CC',
        'beige': '#F5EFE6',
        'sand': '#EAD7A1',
        'ink': '#1F2937',
      },
      boxShadow: {
        soft: '0 6px 16px rgba(0,0,0,0.07)',
        elevated: '0 10px 24px rgba(0,0,0,0.08)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/line-clamp'),
  ],
}

