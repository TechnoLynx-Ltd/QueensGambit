import tensorflow as tf

from tensorflow.keras import Input, layers, Model
from keras.layers import LeakyReLU, LayerNormalization


def create_model(num_convolutions=1):
  
    board_input = Input(
        shape=(8, 8, 12), name="board"
    ) 
    white_move_input = Input(shape=1, name="white_move")
    board_features = board_input
    for i in range(1, num_convolutions+1):
        board_features = layers.Conv2D(filters=32,
                                kernel_size=(3, 3),
                                padding='same')(board_features)
        
        board_features = LeakyReLU()(board_features)
        board_features = LayerNormalization()(board_features)
    
    # board_features = layers.Conv2D(filters=32,
    #                         kernel_size=(5, 5),
    #                         strides=(1, 1),
    #                         padding='valid')(board_features)
    # board_features = LeakyReLU()(board_features)
    # board_features = LayerNormalization()(board_features)

    board_features = layers.Flatten()(board_features)

    x = layers.concatenate([board_features, white_move_input])
    x = layers.Dense(128)(x)
    x = LeakyReLU()(x)
    x = LayerNormalization()(x)

    winner_pred = layers.Dense(3, name="winner", activation='softmax')(x)
    moves_pred = layers.Dense(1, name="moves_left")(x)
    
    model = Model(
        inputs=[board_input, white_move_input],
        outputs=[winner_pred, moves_pred],
    )

    model.summary()

    model.compile(
        optimizer='adam',
        loss={
            "winner": tf.keras.losses.CategoricalCrossentropy(from_logits=False),
            "moves_left": tf.keras.losses.MeanAbsoluteError(),
        }
    )

    return model


if __name__ == '__main__':
    m = create_model()
