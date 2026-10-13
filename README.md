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

## Python Tests

Each Python project keeps unit tests in `tests/unit` and slower tests that use real resources (e.g. puzzle images)
in `tests/integration`, marked with `pytestmark = pytest.mark.integration`. To run one set or the other from a
project's directory:

```
uv run pytest tests -m "not integration"
uv run pytest tests -m integration
```

Pytest runs with `--import-mode=importlib` (set in each project's `pyproject.toml`), so a unit test and an
integration test can share the same file name, e.g. `tests/unit/test_grid_finder.py` and
`tests/integration/test_grid_finder.py`. The trade-off is that test modules cannot import from each other, so
shared fixtures and test helpers belong in a `conftest.py`, which pytest loads automatically for every test in
that directory and below. For example, `create-puzzle/tests/conftest.py` provides the `build_event` and
`lambda_context` fixtures used by its tests.
