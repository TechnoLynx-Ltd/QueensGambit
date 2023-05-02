import tensorflow as tf

from tensorflow.keras import Input, layers, Model
from keras.layers import LeakyReLU, LayerNormalization, Concatenate, Layer
import numpy as np
from tensorflow.python.keras.engine.input_spec import InputSpec
from tensorflow.python.ops import array_ops
from tensorflow.keras.backend import repeat_elements

class RepeatVector3D(Layer):
    """Repeats the input n times.
    Example:
    ```python
    inp = tf.keras.Input(shape=(4,4))
    # now: model.output_shape == (None, 4,4)
    # note: `None` is the batch dimension
    output = RepeatVector3D(3)(inp)
    # now: model.output_shape == (None, 3, 4, 4)
    model = tf.keras.Model(inputs=inp, outputs=output)
    ```
    Args:
        n: Integer, repetition factor.
    Input shape:
        3D tensor of shape `(None, x, y)`.
    Output shape:
        4D tensor of shape `(None, n, x, y)`.
    """

    def __init__(self, n, **kwargs):
        super(RepeatVector3D, self).__init__(**kwargs)
        self.n = n
    
    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        return tensor_shape.TensorShape([input_shape[0], self.n, input_shape[1]])

    def call(self, inputs):
        inputs = array_ops.expand_dims(inputs, 1)
        repeat = repeat_elements(inputs, self.n, axis=1)
        return repeat

    def get_config(self):
        config = {'n': self.n}
        base_config = super(RepeatVector3D, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

def get_result(board_features , out_name = "winner", prev_winner_prediction =None):
    for _ in range(2):
        board_features = layers.DepthwiseConv2D(
                                kernel_size=(3, 3),
                                strides=(2,2),
                                padding='valid')(board_features)
        board_features = LeakyReLU()(board_features)
    board_features = layers.Flatten()(board_features)
    if prev_winner_prediction != None:
        board_features = tf.keras.layers.Concatenate(axis=1)([board_features, prev_winner_prediction])
    on_winner = layers.Dense(3, name=out_name, activation='softmax')(board_features)
    on_moves = layers.Dense(1, name="moves_left")(board_features)
    return on_winner, on_moves

def introduce_winner(winner):
    res = tf.keras.layers.RepeatVector(8)(winner)
    res = RepeatVector3D(8)(res)
    return res


def create_model(num_convolutions_total=1, num_conv_in_block=1):
  
    board_input = Input(
        shape=(8, 8, 13), name="board"
    ) 
    winner_pred_1, moves_pred_1, winner_pred_2, moves_pred_2 = (None, None, None, None)

    board_features = board_input
    for i in range(1, num_convolutions_total+1):
        if i%num_conv_in_block == 0:
            board_features = Concatenate(axis=3)([board_input, board_features])
        board_features = layers.Conv2D(filters=16,
                                kernel_size=(3, 3),
                                padding='same')(board_features)
        
        board_features = LeakyReLU()(board_features)
        board_features = LayerNormalization()(board_features)
        if i == num_convolutions_total//3:
            winner_pred_1, moves_pred_1 = get_result(board_features, "winner_first")
            winner_layer = introduce_winner(winner_pred_1)
            board_features = Concatenate(axis=3)([board_input, winner_layer])
        elif i == 2*num_convolutions_total // 3:
            winner_pred_2, moves_pred_2 = get_result(board_features, "winner_second", prev_winner_prediction = winner_pred_1)
            winner_layer = introduce_winner(winner_pred_2)
            board_features = Concatenate(axis=3)([board_input, winner_layer])

    #apply 3 convolutions with stride 2 and kernel 2x2

    winner_pred, moves_pred = get_result(board_features, prev_winner_prediction = winner_pred_2)
    
    model = Model(
        inputs=[board_input],
        outputs=[winner_pred, moves_pred, winner_pred_1, winner_pred_2],
    )

    model.summary()
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
    model.compile(
        optimizer=optimizer,
        loss={
            "winner": tf.keras.losses.CategoricalCrossentropy(),
            "moves_left": tf.keras.losses.MeanAbsoluteError(),
            "winner_first": tf.keras.losses.CategoricalCrossentropy(),
            "winner_second":tf.keras.losses.CategoricalCrossentropy()
        },
        loss_weights={
            "winner":1,
            "moves_left": 0,
            "winner_first": 1,
            "winner_second": 1
        }
    )

    return model


if __name__ == '__main__':
    m = create_model()
