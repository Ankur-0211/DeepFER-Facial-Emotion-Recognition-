import cv2
import numpy as np

_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_faces(image: np.ndarray) -> list[dict]:
    """image: BGR array (as decoded by cv2.imdecode). Returns bounding boxes
    and grayscale crops ready for the classification model."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    results = []
    for (x, y, w, h) in faces:
        crop = gray[y : y + h, x : x + w]
        results.append(
            {
                "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "crop": crop,
            }
        )
    return results