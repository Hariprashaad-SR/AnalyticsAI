import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api/upload':        { target: 'http://localhost:8000', changeOrigin: true },
      '/api/init-session':  { target: 'http://localhost:8000', changeOrigin: true },
      '/api/query':         { target: 'http://localhost:8000', changeOrigin: true },
      '/api/sessions':      { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
