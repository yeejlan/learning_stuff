const { resolve } = require('path')
const { defineConfig } = require('vite')

module.exports = defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'src/admin.html'),
        test: resolve(__dirname, 'src/test.html'),
        header: resolve(__dirname, 'header.html')
      }
    }
  }
})