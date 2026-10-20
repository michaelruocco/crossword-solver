import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/testSetup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      enabled: true,
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/main.tsx', 'src/testSetup.ts', 'src/**/*.test.ts', 'src/**/*.test.tsx'],
      reportsDirectory: '../../coverage/packages/ui',
      reporter: ['text', ['lcov', { projectRoot: '../..' }]],
      provider: 'v8',
    },
  },
})
