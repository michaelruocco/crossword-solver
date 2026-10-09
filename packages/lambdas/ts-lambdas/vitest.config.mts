import { defineConfig } from 'vitest/config';

export default defineConfig(() => ({
  root: import.meta.dirname,
  cacheDir: '../../../node_modules/.vite/packages/lambdas/ts-lambdas',
  test: {
    name: '@crossword-solver/ts-lambdas',
    watch: false,
    globals: true,
    environment: 'node',
    include: ['{src,tests}/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    reporters: ['default'],
    coverage: {
      enabled: true,
      reportsDirectory: '../../../coverage/packages/lambdas/ts-lambdas',
      // Repo-relative paths in lcov.info so Sonar can resolve them
      reporter: ['text', ['lcov', { projectRoot: '../../..' }] as ['lcov', { projectRoot: string }]],
      provider: 'v8' as const,
    },
  },
}));
