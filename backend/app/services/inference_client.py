import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_ML_DIR = Path(__file__).resolve().parents[3] / "ml"
sys.path.insert(0, str(_ML_DIR))

from inference.engine import InferenceEngine  # noqa: E402
from app.services.face_detection import detect_faces  # noqa: E402

_engine: InferenceEngine | None = None

# All model load + predict calls run on this single dedicated thread, since
# TensorFlow/Keras models loaded on one thread can crash (silently, on Windows)
# if later used from a different thread — which is what FastAPI's default
# threadpool-per-request behavior would otherwise cause.
_inference_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="inference")


def _load_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine(
            model_path=str(_ML_DIR / "inference" / "artifacts" / "best_model.keras"),
            label_map_path=str(_ML_DIR / "data" / "processed" / "label_map.json"),
        )
    return _engine


def preload_model():
    """Call once at app startup, on the main thread's executor, so the model
    is fully loaded and warmed up before any request arrives."""
    _inference_executor.submit(_load_engine).result()


def _predict_faces_sync(image) -> list[dict]:
    engine = _load_engine()
    faces = detect_faces(image)
    results = []
    for face in faces:
        pred = engine.predict(face["crop"])
        results.append(
            {
                "bounding_box": face["bounding_box"],
                "label": pred["label"],
                "confidence": pred["confidence"],
                "class_probabilities": pred["class_probabilities"],
            }
        )
    return results


async def predict_faces_async(image) -> list[dict]:
    """Runs face detection + classification on the dedicated inference thread,
    awaited from an async endpoint so the event loop isn't blocked."""
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_inference_executor, _predict_faces_sync, image)