from tensorflow import keras
from tensorflow.keras import layers


def build_cnn(num_classes: int, input_shape=(48, 48, 1)) -> keras.Model:
    """Lighter 3-block CNN (Conv2D -> BatchNorm -> ReLU -> MaxPool -> Dropout),
    with GlobalAveragePooling instead of a large Flatten+Dense stack, to reduce
    parameter count and overfitting risk for CPU training on 48x48 grayscale data."""
    inputs = keras.Input(shape=input_shape)
    x = inputs

    filters = [32, 64, 128]
    for f in filters:
        x = layers.Conv2D(f, (3, 3), padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.Conv2D(f, (3, 3), padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Dropout(0.3)(x)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    return keras.Model(inputs, outputs, name="deepfer_cnn_v2")