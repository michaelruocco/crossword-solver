import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import { loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), 'VITE_')
  const apiBaseUrl = environment.VITE_API_BASE_URL?.replace(/\/+$/, '')

  return {
    plugins: [react()],
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/testSetup.ts'],
      include: ['src/**/*.test.{ts,tsx}'],
    },
    server: {
      proxy: apiBaseUrl ? { '/v1': { target: apiBaseUrl, changeOrigin: true } } : undefined,
    },
  }
})
