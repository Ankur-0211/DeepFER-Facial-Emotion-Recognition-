import asyncio
import os
import time
import uuid

import requests
import websockets

API_BASE_URL = os.environ.get("API_BASE_URL", " http://127.0.0.1:8000")
WS_BASE_URL = os.environ.get("WS_BASE_URL", "ws://127.0.0.1:8000")
SAMPLE_FACE_PATH = os.environ.get(
    "LOAD_TEST_FACE_IMAGE", os.path.join(os.path.dirname(__file__), "sample_face.jpg")
)
TEST_DURATION_SEC = float(os.environ.get("WS_TEST_DURATION_SEC", "15"))

# NFR target from SDD Section 6: webcam stream >= 10 FPS end-to-end.
TARGET_FPS = 10


def _get_token() -> str:
    email = f"loadtest_ws_{uuid.uuid4().hex[:10]}@example.com"
    password = "LoadTest123!"
    requests.post(f"{API_BASE_URL}/api/v1/auth/register", json={"email": email, "password": password})
    resp = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


async def run():
    if not os.path.exists(SAMPLE_FACE_PATH):
        raise FileNotFoundError(
            f"No sample face image at {SAMPLE_FACE_PATH}. Set LOAD_TEST_FACE_IMAGE."
        )
    with open(SAMPLE_FACE_PATH, "rb") as f:
        frame_bytes = f.read()

    token = _get_token()
    uri = f"{WS_BASE_URL}/ws/v1/stream?token={token}"

    frame_latencies = []
    frames_sent = 0
    start = time.monotonic()

    async with websockets.connect(uri) as ws:
        while time.monotonic() - start < TEST_DURATION_SEC:
            t0 = time.monotonic()
            await ws.send(frame_bytes)
            await ws.recv()  # wait for the prediction response before sending next frame
            frame_latencies.append(time.monotonic() - t0)
            frames_sent += 1

    elapsed = time.monotonic() - start
    achieved_fps = frames_sent / elapsed
    avg_latency_ms = (sum(frame_latencies) / len(frame_latencies)) * 1000
    p95_latency_ms = sorted(frame_latencies)[int(len(frame_latencies) * 0.95)] * 1000

    print(f"\n--- WebSocket stream load test ({elapsed:.1f}s) ---")
    print(f"Frames processed: {frames_sent}")
    print(f"Achieved throughput: {achieved_fps:.2f} FPS  (NFR target: >= {TARGET_FPS} FPS)")
    print(f"Avg per-frame latency: {avg_latency_ms:.1f}ms")
    print(f"p95 per-frame latency: {p95_latency_ms:.1f}ms")
    print("PASS" if achieved_fps >= TARGET_FPS else "FAIL — below NFR target")


if __name__ == "__main__":
    asyncio.run(run())