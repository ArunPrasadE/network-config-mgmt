import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // In Docker Compose: VITE_BACKEND_URL=http://backend:8000 (set in docker-compose.yml)
        // Running locally:   falls back to http://localhost:8000
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
