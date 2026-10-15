# crossword_solver.test_utils

Shared pytest fixtures (`build_event`, `build_sqs_event`, `lambda_context`) and API response helpers for the Lambda tests.

Projects add this library as a dev dependency and import the fixtures in their `tests/conftest.py`:

```python
from crossword_solver_test_utils.fixtures import build_event, lambda_context  # noqa: F401
```
