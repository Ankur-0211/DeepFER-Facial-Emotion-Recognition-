"""
Reads FER-style images directly out of a zip archive (no extraction to disk),
resizes/normalizes them, and writes compact .npz tensors + a label map to
ml/data/processed/.

Expected zip layout (confirmed for this project):
    archive3/train/<class_name>/*.jpg
    archive3/test/<class_name>/*.jpg
    __MACOSX/...   <- ignored
"""

import argparse
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from tqdm import tqdm

IMG_SIZE = 48


def _iter_images(zf: zipfile.ZipFile, split: str):
    """Yield (label_name, PIL.Image) for every valid image under archive3/<split>/."""
    for name in zf.namelist():
        if "__MACOSX" in name:
            continue
        if not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        parts = name.split("/")
        # expect: ["archive3", "train"|"test", "<class>", "<file>.jpg"]
        if len(parts) < 4 or parts[1] != split:
            continue
        label_name = parts[2]
        with zf.open(name) as f:
            data = f.read()
        try:
            img = Image.open(io.BytesIO(data)).convert("L")  # grayscale
        except Exception:
            continue  # skip unreadable/corrupt files instead of crashing the run
        yield label_name, img


def _load_split(zip_path: Path, split: str, label_map: dict[str, int]):
    X, y = [], []
    with zipfile.ZipFile(zip_path, "r") as zf:
        total = sum(
            1
            for n in zf.namelist()
            if "__MACOSX" not in n
            and n.lower().endswith((".jpg", ".jpeg", ".png"))
            and len(n.split("/")) >= 4
            and n.split("/")[1] == split
        )
        for label_name, img in tqdm(
            _iter_images(zf, split), total=total, desc=f"Loading {split}"
        ):
            img = img.resize((IMG_SIZE, IMG_SIZE))
            arr = np.asarray(img, dtype=np.float32) / 255.0
            X.append(arr)
            y.append(label_map[label_name])
    X = np.expand_dims(np.stack(X), axis=-1)  # (N, 48, 48, 1)
    y = np.array(y, dtype=np.int64)
    return X, y


def _discover_label_map(zip_path: Path, split: str) -> dict[str, int]:
    classes = set()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if "__MACOSX" in name:
                continue
            parts = name.split("/")
            if len(parts) >= 4 and parts[1] == split and parts[2]:
                classes.add(parts[2])
    return {name: i for i, name in enumerate(sorted(classes))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", default="ml/data/raw/dataset.zip")
    parser.add_argument("--output-dir", default="ml/data/processed")
    parser.add_argument("--val-split", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    label_map = _discover_label_map(zip_path, "train")
    print(f"Discovered classes: {label_map}")

    X_train_full, y_train_full = _load_split(zip_path, "train", label_map)
    X_test, y_test = _load_split(zip_path, "test", label_map)

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full,
        y_train_full,
        test_size=args.val_split,
        random_state=args.seed,
        stratify=y_train_full,
    )

    np.savez_compressed(out_dir / "train.npz", X=X_train, y=y_train)
    np.savez_compressed(out_dir / "val.npz", X=X_val, y=y_val)
    np.savez_compressed(out_dir / "test.npz", X=X_test, y=y_test)

    with open(out_dir / "label_map.json", "w") as f:
        json.dump(label_map, f, indent=2)

    # Class weights for imbalance handling (e.g. Disgust is typically under-represented)
    counts = np.bincount(y_train, minlength=len(label_map))
    total = counts.sum()
    class_weights = {
        int(i): float(total / (len(label_map) * c)) if c > 0 else 0.0
        for i, c in enumerate(counts)
    }
    with open(out_dir / "class_weights.json", "w") as f:
        json.dump(class_weights, f, indent=2)

    print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    print(f"Class weights: {class_weights}")
    print(f"Saved to {out_dir}/")


if __name__ == "__main__":
    main()