import io
import zipfile
import numpy as np
from PIL import Image

from data.preprocess import _discover_label_map, _load_split, IMG_SIZE


def _build_fake_zip(tmp_path):
    zip_path = tmp_path / "fake.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for split in ("train", "test"):
            for cls in ("happy", "sad"):
                for i in range(3):
                    img = Image.fromarray(
                        (np.random.rand(60, 60) * 255).astype(np.uint8)
                    )
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    zf.writestr(f"archive3/{split}/{cls}/img{i}.jpg", buf.getvalue())
        zf.writestr("__MACOSX/archive3/train/happy/._img0.jpg", b"junk")
    return zip_path


def test_discover_label_map(tmp_path):
    zip_path = _build_fake_zip(tmp_path)
    label_map = _discover_label_map(zip_path, "train")
    assert label_map == {"happy": 0, "sad": 1}


def test_load_split_shapes(tmp_path):
    zip_path = _build_fake_zip(tmp_path)
    label_map = _discover_label_map(zip_path, "train")
    X, y = _load_split(zip_path, "train", label_map)
    assert X.shape == (6, IMG_SIZE, IMG_SIZE, 1)
    assert y.shape == (6,)
    assert X.max() <= 1.0 and X.min() >= 0.0