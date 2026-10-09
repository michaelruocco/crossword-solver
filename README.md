# Crossword Solver

## Building and Deploying to AWS

```
pnpm exec nx run-many -t assemble
./infrastructure/opencv/build-layer.sh
./infrastructure/tesseract/build-layer.sh
terraform -chdir=infrastructure/terraform apply
```
