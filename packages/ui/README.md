# Crossword Atlas UI

React and TypeScript frontend for browsing puzzle summaries.

## Local development

Set `VITE_API_BASE_URL` in `.env.local` to the deployed API Gateway base URL. In development, Vite proxies `/v1` requests to that host so the browser does not need direct API CORS access.

Start the app with:

```sh
pnpm --filter @crossword-solver/ui dev
```

The first screen fetches every puzzle summary page. `ApiClient` also exposes page-level fetching for a future infinite-scroll view. Production builds read the API host from `VITE_API_BASE_URL`.

Build, lint, and test with `pnpm --filter @crossword-solver/ui build`, `pnpm --filter @crossword-solver/ui lint`, and `pnpm --filter @crossword-solver/ui test`.
