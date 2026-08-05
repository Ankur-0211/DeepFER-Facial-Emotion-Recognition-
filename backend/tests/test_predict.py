import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _auth_headers(email: str, password: str = "StrongPass123!") -> dict:
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _sample_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (48, 48), color=(120, 120, 120))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


FAKE_FACES = [
    {
        "label": "happy",
        "confidence": 0.91,
        "bounding_box": {"x": 10, "y": 10, "width": 40, "height": 40},
        "class_probabilities": {"happy": 0.91, "sad": 0.02, "neutral": 0.07},
    },
    {
        "label": "neutral",
        "confidence": 0.55,
        "bounding_box": {"x": 60, "y": 60, "width": 90, "height": 90},
        "class_probabilities": {"happy": 0.1, "sad": 0.05, "neutral": 0.55, "angry": 0.3},
    },
]

async def _fake_predict_faces_async(image):
    return FAKE_FACES


async def _fake_predict_faces_async_empty(image):
    return []


class _FakeVideoCapture:
    """Simulates cv2.VideoCapture without needing a real video file on disk."""

    def __init__(self, path, frame_count=75, fps=25.0):
        self._frame_count = frame_count
        self._fps = fps
        self._idx = 0

    def get(self, prop):
        return self._fps

    def read(self):
        if self._idx >= self._frame_count:
            return False, None
        self._idx += 1
        return True, np.zeros((48, 48, 3), dtype=np.uint8)

    def release(self):
        pass


class TestPredictImage:
    def test_requires_auth(self):
        response = client.post(
            "/api/v1/predict/image",
            files={"file": ("test.jpg", _sample_jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 401

    def test_returns_predictions_for_detected_faces(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async
        )
        headers = _auth_headers("predict_img@example.com")
        response = client.post(
            "/api/v1/predict/image",
            files={"file": ("test.jpg", _sample_jpeg_bytes(), "image/jpeg")},
            headers=headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["predictions"]) == 2
        assert body["predictions"][0]["emotion"] == "happy"
        assert body["predictions"][0]["confidence"] == pytest.approx(0.91)
        assert body["predictions"][0]["boundingBox"] == {"x": 10, "y": 10, "width": 40, "height": 40}

    def test_no_faces_detected_returns_empty_list(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async_empty
        )
        headers = _auth_headers("predict_nofaces@example.com")
        response = client.post(
            "/api/v1/predict/image",
            files={"file": ("test.jpg", _sample_jpeg_bytes(), "image/jpeg")},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["predictions"] == []

    def test_undecodable_file_returns_400(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async
        )
        headers = _auth_headers("predict_baddata@example.com")
        response = client.post(
            "/api/v1/predict/image",
            files={"file": ("test.jpg", b"not an image", "image/jpeg")},
            headers=headers,
        )
        assert response.status_code == 400


class TestPredictVideo:
    def test_requires_auth(self):
        response = client.post(
            "/api/v1/predict/video",
            files={"file": ("test.mp4", b"fake video bytes", "video/mp4")},
        )
        assert response.status_code == 401

    def test_returns_timeline_sampled_once_per_second(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async
        )
        monkeypatch.setattr(
            "app.api.v1.predict.cv2.VideoCapture",
            lambda path: _FakeVideoCapture(path, frame_count=75, fps=25.0),
        )
        headers = _auth_headers("predict_video1@example.com")
        response = client.post(
            "/api/v1/predict/video",
            files={"file": ("test.mp4", b"fake video bytes", "video/mp4")},
            headers=headers,
        )
        assert response.status_code == 200
        timeline = response.json()["timeline"]
        # 75 frames @ 25fps, sampled every 25 frames -> frames 0, 25, 50 = 3 samples
        assert len(timeline) == 3
        assert timeline[0]["timestamp_sec"] == 0.0
        assert timeline[0]["emotion"] == "happy"
        assert timeline[1]["timestamp_sec"] == 1.0

    def test_no_faces_in_video_returns_empty_timeline(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async_empty
        )
        monkeypatch.setattr(
            "app.api.v1.predict.cv2.VideoCapture",
            lambda path: _FakeVideoCapture(path, frame_count=25, fps=25.0),
        )
        headers = _auth_headers("predict_video2@example.com")
        response = client.post(
            "/api/v1/predict/video",
            files={"file": ("test.mp4", b"fake video bytes", "video/mp4")},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["timeline"] == []

    def test_garbage_file_gracefully_degrades_to_empty_timeline(self, monkeypatch):
        # Uses the REAL cv2.VideoCapture (not mocked) to confirm the endpoint's
        # actual documented graceful-degradation behavior on unreadable input.
        monkeypatch.setattr(
            "app.api.v1.predict.predict_faces_async", _fake_predict_faces_async
        )
        headers = _auth_headers("predict_video_garbage@example.com")
        response = client.post(
            "/api/v1/predict/video",
            files={"file": ("test.mp4", b"not a real video file", "video/mp4")},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["timeline"] == []