import io
import os
import uuid

from locust import HttpUser, task, between, events

# Path to a real photo containing a visible face — required for this to
# measure actual CNN inference latency, not just the "no face found" fast path.
SAMPLE_FACE_PATH = os.environ.get(
    "LOAD_TEST_FACE_IMAGE", os.path.join(os.path.dirname(__file__), "sample_face.jpg")
)

# NFR target from SDD Section 6: single-image inference <= 300ms on CPU.
LATENCY_BUDGET_MS = 300


@events.test_start.add_listener
def _check_sample_image(environment, **kwargs):
    if not os.path.exists(SAMPLE_FACE_PATH):
        raise FileNotFoundError(
            f"No sample face image found at {SAMPLE_FACE_PATH}. "
            "Set LOAD_TEST_FACE_IMAGE to a real photo with a visible face — "
            "without one, face detection returns early and this test won't "
            "measure real CNN inference latency."
        )


class DeepFERUser(HttpUser):
    """Simulates a logged-in user repeatedly submitting images for prediction."""

    wait_time = between(0.5, 1.5)

    def on_start(self):
        email = f"loadtest_{uuid.uuid4().hex[:10]}@example.com"
        password = "LoadTest123!"

        register_resp = self.client.post(
            "/api/v1/auth/register", json={"email": email, "password": password}
        )
        if register_resp.status_code != 201:
            print(f"REGISTER FAILED [{register_resp.status_code}]: {register_resp.text}")

        login_resp = self.client.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )
        if login_resp.status_code != 200:
            print(f"LOGIN FAILED [{login_resp.status_code}]: {login_resp.text}")
            self.environment.runner.quit()
            return

        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        with open(SAMPLE_FACE_PATH, "rb") as f:
            self.image_bytes = f.read()

    @task
    def predict_image(self):
        files = {"file": ("face.jpg", io.BytesIO(self.image_bytes), "image/jpeg")}
        with self.client.post(
            "/api/v1/predict/image",
            files=files,
            headers=self.headers,
            catch_response=True,
            name="/api/v1/predict/image",
        ) as response:
            if response.status_code != 200:
                response.failure(f"Got status {response.status_code}")
                return
            if response.elapsed.total_seconds() * 1000 > LATENCY_BUDGET_MS:
                response.failure(
                    f"Exceeded {LATENCY_BUDGET_MS}ms NFR budget: "
                    f"{response.elapsed.total_seconds() * 1000:.0f}ms"
                )
            else:
                response.success()