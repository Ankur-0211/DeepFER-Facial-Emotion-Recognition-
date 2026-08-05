import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _get_token(email: str, password: str = "StrongPass123!") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return login.json()["access_token"]


def _sample_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (48, 48), color=(120, 120, 120))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


FAKE_FACES = [
    {
        "label": "surprise",
        "confidence": 0.77,
        "bounding_box": {"x": 5, "y": 5, "width": 30, "height": 30},
        "class_probabilities": {"surprise": 0.77, "fear": 0.23},
    }
]


async def _fake_predict_faces_async(image):
    return FAKE_FACES


async def _fake_predict_faces_async_empty(image):
    return []


class TestWebSocketAuth:
    def test_invalid_token_closes_with_4401(self):
        import pytest
        from starlette.websockets import WebSocketDisconnect

        # The endpoint closes the socket before ever calling accept() on an
        # invalid token, so the disconnect is raised on connect itself, not
        # on a later receive call.
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws/v1/stream?token=not-a-real-token"):
                pass
        assert exc_info.value.code == 4401

    def test_missing_token_returns_422(self):
        # token is a required Query param; omitting it should fail the
        # WebSocket handshake at the routing/validation layer.
        import pytest
        from starlette.websockets import WebSocketDisconnect

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws/v1/stream") as ws:
                ws.receive_json()


class TestWebSocketStreaming:
    def test_valid_frame_returns_predictions(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.ws_stream.predict_faces_async", _fake_predict_faces_async
        )
        token = _get_token("ws_stream1@example.com")
        with client.websocket_connect(f"/ws/v1/stream?token={token}") as ws:
            ws.send_bytes(_sample_jpeg_bytes())
            response = ws.receive_json()
            assert len(response["predictions"]) == 1
            pred = response["predictions"][0]
            assert pred["emotion"] == "surprise"
            assert pred["confidence"] == 0.77
            assert pred["boundingBox"] == {"x": 5, "y": 5, "width": 30, "height": 30}

    def test_invalid_frame_bytes_returns_error_and_stream_continues(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.ws_stream.predict_faces_async", _fake_predict_faces_async
        )
        token = _get_token("ws_stream2@example.com")
        with client.websocket_connect(f"/ws/v1/stream?token={token}") as ws:
            ws.send_bytes(b"not a real jpeg")
            error_response = ws.receive_json()
            assert error_response == {"error": "invalid frame"}

            # Confirm the connection survives a bad frame and keeps working —
            # this is the "resilient stream" behavior the endpoint promises.
            ws.send_bytes(_sample_jpeg_bytes())
            good_response = ws.receive_json()
            assert good_response["predictions"][0]["emotion"] == "surprise"

    def test_no_faces_detected_returns_empty_predictions(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.ws_stream.predict_faces_async", _fake_predict_faces_async_empty
        )
        token = _get_token("ws_stream3@example.com")
        with client.websocket_connect(f"/ws/v1/stream?token={token}") as ws:
            ws.send_bytes(_sample_jpeg_bytes())
            response = ws.receive_json()
            assert response["predictions"] == []

    def test_multiple_frames_in_sequence(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.ws_stream.predict_faces_async", _fake_predict_faces_async
        )
        token = _get_token("ws_stream4@example.com")
        with client.websocket_connect(f"/ws/v1/stream?token={token}") as ws:
            for _ in range(3):
                ws.send_bytes(_sample_jpeg_bytes())
                response = ws.receive_json()
                assert response["predictions"][0]["emotion"] == "surprise"