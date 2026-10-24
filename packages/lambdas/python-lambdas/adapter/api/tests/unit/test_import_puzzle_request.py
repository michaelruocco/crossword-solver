import pytest

from crossword_solver_adapter_api.import_puzzle_request import ImportPuzzleRequest


@pytest.mark.parametrize("url", ["https://example.com/puzzle.jpg", "http://example.com/puzzle.jpg"])
def test_accepts_http_and_https_urls(url):
    assert ImportPuzzleRequest.model_validate({"imageUrl": url}).image_url == url


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/puzzle.jpg", "example.com/puzzle.jpg", ""])
def test_rejects_other_urls(url):
    with pytest.raises(ValueError, match="imageUrl must be an http or https URL"):
        ImportPuzzleRequest.model_validate({"imageUrl": url})
