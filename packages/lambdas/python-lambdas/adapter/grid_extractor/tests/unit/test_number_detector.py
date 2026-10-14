import logging

import numpy as np
import pytesseract
import pytest

from crossword_solver_adapter_grid_extractor.number_detector import NumberDetector

TESSDATA_DIR = "/opt/share/tessdata"


@pytest.fixture
def ocr(monkeypatch):
    calls = []
    result = {"text": ""}

    def image_to_string(image, lang=None, config=""):
        calls.append({"image": image, "lang": lang, "config": config})
        if isinstance(result["text"], Exception):
            raise result["text"]
        return result["text"]

    monkeypatch.setattr(pytesseract, "image_to_string", image_to_string)

    class Ocr:
        def returns(self, text):
            result["text"] = text

        @property
        def calls(self):
            return calls

    return Ocr()


@pytest.fixture
def detector() -> NumberDetector:
    return NumberDetector(TESSDATA_DIR)


@pytest.fixture
def cell() -> np.ndarray:
    return np.full((20, 20, 3), 255, dtype=np.uint8)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("12", 12), ("7\n", 7), ("  105 \n\f", 105), ("07", 7)],
    ids=["number", "trailing newline", "surrounding whitespace", "leading zero"],
)
def test_detect_returns_number(detector, ocr, cell, text, expected):
    ocr.returns(text)

    assert detector.detect(cell) == expected


@pytest.mark.parametrize("text", ["", " \n", "1a", "1 2", "-3", "\u0661"], ids=repr)
def test_detect_returns_none_when_text_is_not_a_number(detector, ocr, cell, text):
    ocr.returns(text)

    assert detector.detect(cell) is None


def test_detect_returns_none_and_logs_when_tesseract_fails(detector, ocr, cell, caplog):
    ocr.returns(pytesseract.TesseractError(1, "boom"))

    with caplog.at_level(logging.ERROR):
        result = detector.detect(cell)

    assert result is None
    assert "Failed to read number from cell" in caplog.text


def test_detect_reads_a_single_word_of_digits_in_english_using_tessdata_dir(detector, ocr, cell):
    ocr.returns("1")

    detector.detect(cell)

    call = ocr.calls[0]
    assert call["lang"] == "eng"
    assert call["config"].split() == [
        "--psm",
        "8",
        "--oem",
        "1",
        "-c",
        "tessedit_char_whitelist=0123456789",
        "-c",
        "user_defined_dpi=300",
        "--tessdata-dir",
        TESSDATA_DIR,
    ]


def test_detect_quotes_tessdata_dir_containing_spaces(ocr, cell):
    ocr.returns("1")

    NumberDetector("/opt/share/my tessdata").detect(cell)

    assert ocr.calls[0]["config"].endswith("--tessdata-dir '/opt/share/my tessdata'")


def test_detect_converts_colour_cells_from_bgr_to_rgb(detector, ocr):
    ocr.returns("1")
    blue = np.zeros((2, 2, 3), dtype=np.uint8)
    blue[:, :] = (255, 0, 0)

    detector.detect(blue)

    assert ocr.calls[0]["image"][0, 0].tolist() == [0, 0, 255]


def test_detect_passes_grayscale_cells_unchanged(detector, ocr):
    ocr.returns("1")
    gray = np.full((2, 2), 128, dtype=np.uint8)

    detector.detect(gray)

    assert ocr.calls[0]["image"] is gray


def test_detect_logs_text_and_duration_of_tesseract_call(detector, ocr, cell, caplog):
    ocr.returns("12\n")

    with caplog.at_level(logging.INFO):
        detector.detect(cell)

    record = next(record for record in caplog.records if record.message.startswith("Tesseract read"))
    assert record.tesseract_text == "12"
    assert isinstance(record.tesseract_duration_ms, int)
    assert record.tesseract_duration_ms >= 0
