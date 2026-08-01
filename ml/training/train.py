import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json

import numpy as np
from tensorflow import keras

from models.cnn import build_cnn

DATA_DIR = Path("data/processed")
ARTIFACT_DIR = Path("inference/artifacts")


def load_npz(name):
    d = np.load(DATA_DIR / name)
    return d["X"], d["y"]


def oversample_minority_classes(X, y, target_ratio: float = 0.5, seed: int = 42):
    """Duplicate samples from under-represented classes (e.g. disgust) so each
    class has at least target_ratio * (largest class count) samples. Combined
    with per-epoch random augmentation in the ImageDataGenerator, duplicates
    aren't seen identically twice, which limits pure memorization risk."""
    rng = np.random.default_rng(seed)
    counts = np.bincount(y)
    target = int(counts.max() * target_ratio)

    X_parts, y_parts = [X], [y]
    for cls, count in enumerate(counts):
        if count == 0 or count >= target:
            continue
        needed = target - count
        cls_indices = np.where(y == cls)[0]
        extra_indices = rng.choice(cls_indices, size=needed, replace=True)
        X_parts.append(X[extra_indices])
        y_parts.append(y[extra_indices])

    X_balanced = np.concatenate(X_parts, axis=0)
    y_balanced = np.concatenate(y_parts, axis=0)

    shuffle_idx = rng.permutation(len(y_balanced))
    return X_balanced[shuffle_idx], y_balanced[shuffle_idx]


def load_gentle_class_weights(max_weight: float = 2.0, min_weight: float = 0.7) -> dict[int, float]:
    """With oversampling already correcting the bulk of the imbalance, class
    weights only need to nudge, not compensate for a 10x gap on their own."""
    with open(DATA_DIR / "class_weights.json") as f:
        raw = {int(k): v for k, v in json.load(f).items()}
    return {k: float(np.clip(v, min_weight, max_weight)) for k, v in raw.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--early-stopping-patience", type=int, default=12)
    parser.add_argument("--lr-patience", type=int, default=5)
    parser.add_argument("--oversample-ratio", type=float, default=0.5)
    args = parser.parse_args()

    X_train, y_train = load_npz("train.npz")
    X_val, y_val = load_npz("val.npz")

    print("Original class counts:", np.bincount(y_train))
    X_train, y_train = oversample_minority_classes(X_train, y_train, args.oversample_ratio)
    print("Balanced class counts:", np.bincount(y_train))

    with open(DATA_DIR / "label_map.json") as f:
        label_map = json.load(f)
    class_weights = load_gentle_class_weights()
    print(f"Using gentle class weights: {class_weights}")

    model = build_cnn(len(label_map))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    datagen = keras.preprocessing.image.ImageDataGenerator(
        rotation_range=15, zoom_range=0.1, horizontal_flip=True
    )
    train_flow = datagen.flow(X_train, y_train, batch_size=64)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = ARTIFACT_DIR / "best_model.keras"

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=args.early_stopping_patience,
            restore_best_weights=True,
        ),
        keras.callbacks.ModelCheckpoint(
            str(checkpoint_path), monitor="val_accuracy", save_best_only=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=args.lr_patience, min_lr=1e-6
        ),
    ]

    history = model.fit(
        train_flow,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        class_weight=class_weights,
        callbacks=callbacks,
    )

    with open(ARTIFACT_DIR / "training_history.json", "w") as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)

    print(f"Best model saved to {checkpoint_path}")


if __name__ == "__main__":
    main()