import logging
import re
import shlex
from pathlib import Path

import cv2
import numpy as np
import pytesseract

logger = logging.getLogger(__name__)

_NUMBER = re.compile(r"[0-9]+")


class NumberDetector:
    LANGUAGE = "eng"
    # Treat the image as a single word, use the LSTM engine only, and only recognise digits.
    CONFIG = "--psm 8 --oem 1 -c tessedit_char_whitelist=0123456789 -c user_defined_dpi=300"

    def __init__(self, tessdata_dir: str | Path):
        self.config = f"{self.CONFIG} --tessdata-dir {shlex.quote(str(tessdata_dir))}"

    def detect(self, cell: np.ndarray) -> int | None:
        try:
            text = pytesseract.image_to_string(self._to_rgb(cell), lang=self.LANGUAGE, config=self.config).strip()
        except pytesseract.TesseractError:
            logger.exception("Failed to read number from cell")
            return None
        logger.debug("Detected text %r", text)
        if not _NUMBER.fullmatch(text):
            return None
        return int(text)

    @staticmethod
    def _to_rgb(cell: np.ndarray) -> np.ndarray:
        if cell.ndim == 3:
            return cv2.cvtColor(cell, cv2.COLOR_BGR2RGB)
        return cell
