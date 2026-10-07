// Build: npx tailwindcss@3.4.17 -c tailwind.config.js -i tailwind.in.css -o assets/tailwind.css --minify
// Rerun after adding Tailwind classes to any page or generator.
module.exports = {
  content: ['./**/*.html', './**/*.js', './*.py', '!./design-mockups/**', '!./node_modules/**'],
  theme: {
    extend: {
      colors: { darkBg: '#0a0a12', panelBg: '#13131f', brandPink: '#D946EF', brandBlue: '#3B82F6', brandGreen: '#39FF14', brandRed: '#EF4444' },
      fontFamily: { mono: ['"JetBrains Mono"', 'monospace'], sans: ['Inter', 'sans-serif'] },
    },
  },
}
