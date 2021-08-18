const purgecss = require('@fullhuman/postcss-purgecss')

module.exports = {
  plugins: [
    purgecss({
      content: ['index.html'],
      safelist: [/^tooltip-/,/^popover-/]
    })
  ]
}