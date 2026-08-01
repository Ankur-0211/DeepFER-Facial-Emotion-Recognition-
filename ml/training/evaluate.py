import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow import keras

DATA_DIR = Path("data/processed")
ARTIFACT_DIR = Path("inference/artifacts")
DOCS_DIR = Path("../docs")


def main():
    model = keras.models.load_model(ARTIFACT_DIR / "best_model.keras")

    d = np.load(DATA_DIR / "test.npz")
    X_test, y_test = d["X"], d["y"]

    with open(DATA_DIR / "label_map.json") as f:
        label_map = json.load(f)
    idx_to_label = {v: k for k, v in label_map.items()}
    class_names = [idx_to_label[i] for i in range(len(label_map))]

    y_prob = model.predict(X_test)
    y_pred = np.argmax(y_prob, axis=1)

    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
    test_accuracy = report["accuracy"]

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("DeepFER Confusion Matrix")
    plt.tight_layout()
    DOCS_DIR.mkdir(exist_ok=True)
    plt.savefig(DOCS_DIR / "confusion_matrix.png")

    with open(DOCS_DIR / "model_evaluation_report.md", "w") as f:
        f.write("# DeepFER Model Evaluation Report\n\n")
        f.write(f"**Test Accuracy:** {test_accuracy:.4f}\n\n")
        f.write("## Per-Class Metrics\n\n")
        f.write("| Class | Precision | Recall | F1-score |\n|---|---|---|---|\n")
        for name in class_names:
            m = report[name]
            f.write(f"| {name} | {m['precision']:.2f} | {m['recall']:.2f} | {m['f1-score']:.2f} |\n")
        f.write("\n![Confusion Matrix](confusion_matrix.png)\n")

    # Registers this run as a model_versions candidate for Phase 3's table (inserted via backend in a later phase)
    with open(ARTIFACT_DIR / "model_metadata.json", "w") as f:
        json.dump(
            {"test_accuracy": test_accuracy, "artifact_path": "inference/artifacts/best_model.keras"},
            f,
            indent=2,
        )

    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Report written to {DOCS_DIR / 'model_evaluation_report.md'}")


if __name__ == "__main__":
    main()