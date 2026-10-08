import pytest

from crossword_solver_image.url_converter import UrlConverter


@pytest.fixture
def converter():
    return UrlConverter()


def test_to_filename(converter):
    url = "https://example.com/puzzles/puzzle14.jpg"

    filename = converter.to_filename(url)

    assert filename == "puzzle14.jpg"


def test_to_filename_with_query_parameters(converter):
    url = "https://example.com/puzzles/puzzle14.jpg?foo=bar"

    filename = converter.to_filename(url)

    assert filename == "puzzle14.jpg"


def test_to_filename_excluding_extension(converter):
    url = "https://example.com/puzzles/puzzle14.jpg"

    filename_excluding_extension = converter.to_filename_excluding_extension(url)

    assert filename_excluding_extension == "puzzle14"


def test_to_extension(converter):
    url = "https://example.com/puzzles/puzzle14.jpg"

    extension = converter.to_extension(url)

    assert extension == ".jpg"
