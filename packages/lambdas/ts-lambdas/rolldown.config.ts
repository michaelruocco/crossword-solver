import { defineConfig } from 'rolldown';

export default defineConfig([
  {
    tsconfig: 'tsconfig.lib.json',
    input: 'src/create-attempt/create-attempt.ts',
    output: {
      file: '../../../dist/packages/lambdas/ts-lambdas/bundle/lambda/create-attempt/index.js',
      format: 'cjs',
      codeSplitting: false,
    },
    platform: 'node',
    external: [/@aws-sdk\/.*/],
  },
  {
    tsconfig: 'tsconfig.lib.json',
    input: 'src/automatic-answers/automatic-answers.ts',
    output: {
      file: '../../../dist/packages/lambdas/ts-lambdas/bundle/lambda/automatic-answers/index.js',
      format: 'cjs',
      codeSplitting: false,
    },
    platform: 'node',
    external: [/@aws-sdk\/.*/],
  },
]);