// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  base: '/static//',  // ← должно совпадать с static_url_prefix
  server: {
    host: 'localhost',
    port: 5173,
    hmr: { clientPort: 5173 }
  },
  build: {
    outDir: resolve(__dirname, '../backend/static/react'),
    manifest: 'manifest.json',
    rollupOptions: {
      input: '/src/main.jsx'  // ваш входной файл
    }
  }
})