import pytest

from crossword_solver_create_puzzle.create_puzzle.create_puzzle_request import CreatePuzzleRequest


@pytest.mark.parametrize("url", ["https://example.com/puzzle.jpg", "http://example.com/puzzle.jpg"])
def test_accepts_http_and_https_urls(url):
    assert CreatePuzzleRequest.model_validate({"imageUrl": url}).image_url == url


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/puzzle.jpg", "example.com/puzzle.jpg", ""])
def test_rejects_other_urls(url):
    with pytest.raises(ValueError, match="imageUrl must be an http or https URL"):
        CreatePuzzleRequest.model_validate({"imageUrl": url})
