import pytest

from crossword_solver_domain_entities.hyphen_normalizer import (
    normalize_hyphens,
)


@pytest.mark.parametrize(
    "value",
    [
        "---Waller-Bridge",
        "- - -Waller-Bridge",
        "-  -   -Waller-Bridge",
        "‒ − - Waller-Bridge",
        " – — ⁃ Waller-Bridge",
    ],
)
def test_normalizes_hyphens_followed_by_text(value):
    assert normalize_hyphens(value) == "- - - Waller-Bridge"


@pytest.mark.parametrize(
    "value",
    [
        "Carla ---",
        "Carla- - -",
        "Carla- -   -",
        "Carla ‒ − -",
        "Carla – — ⁃ ",
    ],
)
def test_normalizes_hyphens_with_leading_text(value):
    assert normalize_hyphens(value) == "Carla - - -"


@pytest.mark.parametrize(
    "value",
    [
        "Carla --- Francis",
        "Carla- - -Francis",
        "Carla- -   -  Francis",
        "Carla  - -   -  Francis",
        "Carla ‒ − - Francis",
        "Carla – — ⁃ Francis",
    ],
)
def test_normalizes_hyphens_with_both_leading_and_trailing_text(value):
    assert normalize_hyphens(value) == "Carla - - - Francis"


def test_normalizes_hyphens_followed_by_comma():
    value = "Carla - - - , model turned musician"

    assert normalize_hyphens(value) == "Carla - - -, model turned musician"
