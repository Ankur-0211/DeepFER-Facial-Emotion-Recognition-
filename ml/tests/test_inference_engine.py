import json
from pathlib import Path

from models.cnn import build_cnn
from inference.engine import InferenceEngine
import numpy as np


def test_inference_engine_predict(tmp_path):
    model = build_cnn(num_classes=2)
    model_path = tmp_path / "tiny_model.keras"
    model.save(model_path)

    label_map_path = tmp_path / "label_map.json"
    with open(label_map_path, "w") as f:
        json.dump({"happy": 0, "sad": 1}, f)

    engine = InferenceEngine(model_path=str(model_path), label_map_path=str(label_map_path))
    fake_face = (np.random.rand(80, 80) * 255).astype("uint8")
    result = engine.predict(fake_face)

    assert result["label"] in {"happy", "sad"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert set(result["class_probabilities"].keys()) == {"happy", "sad"}