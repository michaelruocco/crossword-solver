import pytest

from crossword_solver_domain_use_case.log_sanitizer import sanitize_for_log


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("plain", "plain"),
        ("line one\nline two", "line oneline two"),
        ("carriage\rreturn", "carriagereturn"),
        ("windows\r\nnewline", "windowsnewline"),
        (123, "123"),
    ],
)
def test_sanitize_for_log_removes_line_breaks(value, expected):
    assert sanitize_for_log(value) == expected
