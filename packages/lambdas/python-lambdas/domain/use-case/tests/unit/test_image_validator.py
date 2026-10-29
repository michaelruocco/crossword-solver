import pytest
from crossword_solver_domain_entities.image_file import ImageFile
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


@pytest.mark.parametrize("image_format", [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".PNG", ".WEBP", "jpg"])
def test_validate_accepts_default_allowed_formats(image_format):
    ImageValidator().validate(an_image(image_format=image_format))


@pytest.mark.parametrize("filename", ["puzzle14.png", "puzzle.webp", "puzzle.WEBP"])
def test_validate_filename_accepts_an_allowed_format_without_any_content(filename):
    ImageValidator().validate_filename(filename)


@pytest.mark.parametrize(
    ("filename", "message"),
    [("puzzle14.gif", "image format gif is not an allowed format"), ("", "file name is mandatory")],
)
def test_validate_filename_rejects_invalid_filenames(filename, message):
    validator = ImageValidator()

    with pytest.raises(InvalidImageError, match=message):
        validator.validate_filename(filename)


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


@pytest.mark.parametrize("image_format", [".gif", ".pdf", "", "."])
def test_validate_raises_error_when_format_is_not_allowed(image_format):
    validator = ImageValidator()
    image = an_image(image_format=image_format)

    with pytest.raises(InvalidImageError, match="is not an allowed format png,jpg,jpeg,webp"):
        validator.validate(image)


def test_validate_includes_the_rejected_format_in_the_error():
    validator = ImageValidator()
    image = an_image(image_format=".GIF")

    with pytest.raises(InvalidImageError, match="image format gif is not an allowed format"):
        validator.validate(image)


def test_validate_raises_error_when_image_is_larger_than_the_maximum_size():
    validator = ImageValidator(max_size_in_mb=1)
    image = an_image(size_in_bytes=ONE_MB + 1)

    with pytest.raises(InvalidImageError, match="image file is larger than max allowed file size 1 MB"):
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


def test_max_size_in_bytes_is_the_maximum_size_in_mb_converted():
    assert ImageValidator(max_size_in_mb=2).max_size_in_bytes == 2 * ONE_MB


@pytest.mark.parametrize("filename", ["puzzle14.JPG", "puzzle.webp", "puzzle.WEBP"])
def test_validate_file_accepts_a_valid_file(filename):
    ImageValidator().validate_file(ImageFile(filename, b"image-bytes"))


@pytest.mark.parametrize(
    ("file", "message"),
    [
        (ImageFile("", b"image-bytes"), "file name is mandatory"),
        (ImageFile(".jpg", b"image-bytes"), "is not an allowed format"),
        (ImageFile("puzzle14.gif", b"image-bytes"), "image format gif is not an allowed format"),
        (ImageFile("puzzle14", b"image-bytes"), "is not an allowed format"),
        (ImageFile("puzzle14.jpg", b""), "image file is empty"),
    ],
    ids=["no filename", "dotfile", "format not allowed", "no extension", "empty"],
)
def test_validate_file_raises_error_for_an_invalid_file(file, message):
    validator = ImageValidator()

    with pytest.raises(InvalidImageError, match=message):
        validator.validate_file(file)


def test_validate_file_raises_error_when_file_is_larger_than_the_maximum_size():
    validator = ImageValidator(max_size_in_mb=1)
    file = ImageFile("puzzle14.jpg", b"x" * (ONE_MB + 1))

    with pytest.raises(InvalidImageError, match="image file is larger than max allowed file size 1 MB"):
        validator.validate_file(file)
