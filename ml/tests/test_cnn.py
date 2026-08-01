import numpy as np
from models.cnn import build_cnn


def test_cnn_output_shape():
    model = build_cnn(num_classes=7)
    dummy_input = np.random.rand(2, 48, 48, 1).astype("float32")
    output = model.predict(dummy_input, verbose=0)
    assert output.shape == (2, 7)
    assert np.allclose(output.sum(axis=1), 1.0, atol=1e-4)  # softmax sums to 1