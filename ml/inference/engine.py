import json
from pathlib import Path

import numpy as np
from PIL import Image
from tensorflow import keras

IMG_SIZE = 48


class InferenceEngine:
    """Loads a trained model once and serves predict(image) calls.
    Consumed by the backend's InferenceClient in Phase 6."""

    def __init__(self, model_path: str = "ml/inference/artifacts/best_model.keras",
                 label_map_path: str = "ml/data/processed/label_map.json"):
        self.model = keras.models.load_model(model_path)
        with open(label_map_path) as f:
            label_map = json.load(f)
        self.idx_to_label = {v: k for k, v in label_map.items()}

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        img = Image.fromarray(image).convert("L").resize((IMG_SIZE, IMG_SIZE))
        arr = np.asarray(img, dtype=np.float32) / 255.0
        return arr.reshape(1, IMG_SIZE, IMG_SIZE, 1)

    def predict(self, image: np.ndarray) -> dict:
        """image: numpy array (H, W) or (H, W, 3) — a single already-cropped face."""
        x = self._preprocess(image)
        probs = self.model.predict(x, verbose=0)[0]
        top_idx = int(np.argmax(probs))
        return {
            "label": self.idx_to_label[top_idx],
            "confidence": float(probs[top_idx]),
            "class_probabilities": {
                self.idx_to_label[i]: float(p) for i, p in enumerate(probs)
            },
        }