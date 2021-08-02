import { defineConfig } from 'windicss/helpers'

module.exports = {
  theme: {
    colors: {
      red: {
        medium: '#e53e3e',
        dark: '#742a2a'
      },
      blue: {
        medium: '#3182ce',
        dark: '#2a4365'
      },
      'th-primary': 'var(--primary)',
      'th-secondary': 'var(--secondary)'
    }
  }
}

export default defineConfig({
  extract: {
    include: ['src/**/*.{vue,html,jsx,tsx}'],
    exclude: ['node_modules', '.git'],
  },
})