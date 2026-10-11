import cv2
import numpy as np


def test_opencv_is_available():
    image = np.zeros((4, 6, 3), dtype=np.uint8)

    resized = cv2.resize(image, (3, 2))

    assert resized.shape == (2, 3, 3)
