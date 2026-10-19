import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/  (vitest/config's defineConfig = Vite's, plus the `test` block)
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward /api/* from the dev server to FastAPI, so the browser sees a single
    // origin (no CORS in dev) and the app can always call relative URLs like /api/health.
    // In production a reverse proxy / load balancer does the same routing.
    proxy: {
      '/api': process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom', // a simulated DOM in Node, so components can render
    setupFiles: ['./src/test/setup.ts'],
  },
})
