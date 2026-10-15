from datetime import UTC

from crossword_solver_domain_use_case.clock import system_clock


def test_system_clock_returns_current_time_in_utc():
    assert system_clock().tzinfo == UTC
