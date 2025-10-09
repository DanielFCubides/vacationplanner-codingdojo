import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api/keycloak': {
        target: 'https://keycloak.dfcubidesc.com',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api\/keycloak/, ''),
      }
    }
  }
})