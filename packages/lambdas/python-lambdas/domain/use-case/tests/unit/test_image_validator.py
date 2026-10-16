import pytest
from PIL import Image as PILImage

from crossword_solver_domain_use_case.image import Image
from crossword_solver_domain_use_case.image_error import ImageError
from crossword_solver_domain_use_case.image_validator import ImageValidator
from crossword_solver_domain_use_case.invalid_image_error import InvalidImageError

ONE_MB = 1024 * 1024


def an_image(name: str = "puzzle14", image_format: str = ".jpg", size_in_bytes: int = 10) -> Image:
    return Image(
        name=name,
        format=image_format,
        pil_image=PILImage.new("RGB", (1, 1)),
        bytes=b"x" * size_in_bytes,
        hash="hash",
    )


@pytest.mark.parametrize("image_format", [".jpg", ".jpeg", ".png", ".JPG", ".PNG", "jpg"])
def test_validate_accepts_default_allowed_formats(image_format):
    ImageValidator().validate(an_image(image_format=image_format))


def test_validate_accepts_an_image_of_exactly_the_maximum_size():
    validator = ImageValidator(max_size_in_mb=1)

    validator.validate(an_image(size_in_bytes=ONE_MB))


def test_validate_raises_error_when_name_is_missing():
    validator = ImageValidator()
    image = an_image(name="")

    with pytest.raises(InvalidImageError, match="file name is mandatory"):
        validator.validate(image)


def test_validate_raises_error_when_image_is_empty():
    validator = ImageValidator()
    image = an_image(size_in_bytes=0)

    with pytest.raises(InvalidImageError, match="image file is empty"):
        validator.validate(image)


def test_validate_accepts_an_image_of_one_byte():
    ImageValidator().validate(an_image(size_in_bytes=1))


@pytest.mark.parametrize("image_format", [".gif", ".pdf", ".webp", "", "."])
def test_validate_raises_error_when_format_is_not_allowed(image_format):
    validator = ImageValidator()
    image = an_image(image_format=image_format)

    with pytest.raises(InvalidImageError, match="is not an allowed format png,jpg,jpeg"):
        validator.validate(image)


def test_validate_includes_the_rejected_format_in_the_error():
    validator = ImageValidator()
    image = an_image(image_format=".GIF")

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        validator.validate(image)


def test_validate_raises_error_when_image_is_larger_than_the_maximum_size():
    validator = ImageValidator(max_size_in_mb=1)
    image = an_image(size_in_bytes=ONE_MB + 1)

    with pytest.raises(InvalidImageError, match="image file size 1.00 MB is larger than max allowed file size 1 MB"):
        validator.validate(image)


def test_validate_allows_up_to_twenty_mb_by_default():
    validator = ImageValidator()
    image = an_image(size_in_bytes=20 * ONE_MB + 1)

    with pytest.raises(InvalidImageError, match="larger than max allowed file size 20 MB"):
        validator.validate(image)


def test_validate_uses_given_allowed_formats():
    validator = ImageValidator(allowed_formats=["GIF"])

    validator.validate(an_image(image_format=".gif"))


def test_invalid_image_error_is_an_image_error():
    assert issubclass(InvalidImageError, ImageError)
