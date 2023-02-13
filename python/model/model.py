import tensorflow as tf

from tensorflow.keras import datasets, layers, models


def create_model():
    model = models.Sequential()
    model.add(layers.Conv2D(filters=32,
                            kernel_size=(3, 3),
                            padding='same',
                            activation='relu',
                            input_shape=(8, 8, 12)))
    # model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(filters=32,
                            kernel_size=(5, 5),
                            strides=(1, 1),
                            padding='valid',
                            activation='relu'))
    # model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(2))
    model.add(tf.keras.layers.Softmax())

    model.summary()

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    return model


if __name__ == '__main__':
    m = create_model()
