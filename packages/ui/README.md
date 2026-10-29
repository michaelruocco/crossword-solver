# Crossword Atlas UI

React and TypeScript frontend for browsing puzzle summaries.

Add puzzles using **Upload puzzle** for a local image file or **Import from URL** for a direct HTTP/HTTPS image URL. URL imports use `POST /v1/puzzles/imports` with an `imageUrl` payload. Both flows poll the import status and refresh the library when processing completes.

## Local development

Set `VITE_API_BASE_URL` in `.env.local` to the API Gateway base URL. The browser sends API requests directly to that host in development and production; the API and image bucket allow the local UI origins through CORS.

Start the app with:

```sh
pnpm --filter @crossword-solver/ui dev
```

The first screen fetches every puzzle summary page. `ApiClient` also exposes page-level fetching for a future infinite-scroll view. Production builds read the API host from `VITE_API_BASE_URL`.

Build, lint, and test with `pnpm --filter @crossword-solver/ui build`, `pnpm --filter @crossword-solver/ui lint`, and `pnpm --filter @crossword-solver/ui test`.

## AWS deployment

With Terraform and AWS CLI credentials configured for the target account, create the private bucket and CloudFront distribution:

```sh
terraform -chdir=infrastructure/terraform apply
```

After Terraform finishes, build the UI with the deployed API URL, upload the static files, and invalidate CloudFront:

```sh
pnpm nx run crossword_solver.ui:deploy
terraform -chdir=infrastructure/terraform output -raw ui_url
```

The first CloudFront distribution deployment can take several minutes to become available.
