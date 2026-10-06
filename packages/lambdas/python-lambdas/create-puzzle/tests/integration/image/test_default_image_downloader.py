import pytest

from crossword_solver_create_puzzle.create_puzzle.image.default_image_downloader import (
    DefaultImageDownloader,
)
from crossword_solver_create_puzzle.create_puzzle.image.image_error import ImageError

@pytest.fixture
def downloader():
    return DefaultImageDownloader()


@pytest.mark.integration
def test_download_image(downloader):
    url = "https://hackathon.caci.co.uk/images/puzzle24.jpg"

    image = downloader.download_image(url)

    assert image.name == "puzzle24"
    assert image.format == ".jpg"
    assert image.image is not None
    assert image.bytes
    assert image.hash


@pytest.mark.integration
def test_download_image_not_found(downloader):
    with pytest.raises(ImageError, match="Failed to download image"):
        downloader.download_image(
            "https://hackathon.caci.co.uk/images/does-not-exist.jpg"
        )