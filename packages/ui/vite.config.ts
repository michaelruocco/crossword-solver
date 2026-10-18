import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import { loadEnv } from 'vite'

function trimTrailingSlashes(value: string): string {
  let end = value.length
  while (end > 0 && value[end - 1] === '/') end--
  return value.slice(0, end)
}

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), 'VITE_')
  const apiBaseUrl = environment.VITE_API_BASE_URL && trimTrailingSlashes(environment.VITE_API_BASE_URL)

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
