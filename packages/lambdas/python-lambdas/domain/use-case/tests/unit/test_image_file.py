import pytest

from crossword_solver_domain_use_case.image_file import ImageFile


@pytest.mark.parametrize(
    ("filename", "name", "image_format"),
    [
        ("puzzle14.jpg", "puzzle14", ".jpg"),
        ("puzzle14.JPG", "puzzle14", ".JPG"),
        ("puzzle.14.png", "puzzle.14", ".png"),
        ("puzzle14", "puzzle14", ""),
        (".jpg", ".jpg", ""),
        ("", "", ""),
    ],
)
def test_name_and_format_come_from_the_filename(filename, name, image_format):
    file = ImageFile(filename, b"image-bytes")

    assert file.name == name
    assert file.format == image_format
