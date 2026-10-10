# Crossword Solver

[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=coverage)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=michaelruocco_crossword-solver&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=michaelruocco_crossword-solver)

## Building and Deploying to AWS

```
pnpm exec nx run-many -t assemble
./infrastructure/opencv/build-layer.sh
./infrastructure/tesseract/build-layer.sh
terraform -chdir=infrastructure/terraform apply
```

## Scaffolding New Projects

The projects in this repo were generated with [@aws/nx-plugin](https://www.npmjs.com/package/@aws/nx-plugin)
(see the `metadata.generator` entries in each `project.json`). The plugin is only needed to run its
generators, so it is not kept as a dependency: it pins older Nx versions, which pull in outdated
transitive dependencies (e.g. a vulnerable `axios`) and cause peer dependency conflicts.

To scaffold a new project, add it temporarily, run the generator, then remove it again:

```
pnpm add -D @aws/nx-plugin
pnpm exec nx g @aws/nx-plugin:py#lambda-function   # or ts#lambda-function, py#project, etc.
pnpm remove @aws/nx-plugin
pnpm dedupe
```

`pnpm dedupe` clears any older Nx packages the plugin left in the lockfile.
