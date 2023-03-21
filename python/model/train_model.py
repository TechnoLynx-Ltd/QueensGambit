import numpy as np
from sklearn.model_selection import train_test_split
import tensorflowjs as tfjs
from model import create_model
from tensorflow.keras.callbacks import TensorBoard
import tensorflow as tf
import os
import shutil
from tqdm import tqdm

def train(model, X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,
                y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir,
                tensorboard_dir = "./logs"):
    try:
        os.mkdir(tensorboard_dir)
    except OSError as error:
        shutil.rmtree(tensorboard_dir)
        os.mkdir(tensorboard_dir)
    tensorboard_callback = TensorBoard(log_dir=tensorboard_dir, histogram_freq=1)
    with tf.device('/gpu:0'):
        history = model.fit(
            {"board": X_pos_train, "white_move": X_white_move_train},
            {"winner": y_result_train, "moves_left": y_moves_train},
            epochs=20,
            batch_size=128,
            validation_data=(
                {"board": X_pos_test, "white_move": X_white_move_test},
                {"winner": y_result_test, "moves_left": y_moves_test}
                ),
            shuffle=True,
            callbacks = [tensorboard_callback]
            )

    print(history.history)
    tfjs.converters.save_keras_model(model, tfjs_target_dir)
    return model


if __name__ == '__main__':
    X_position = np.load("../../data/npy/X_positions.npy").astype(np.int8)
    X_position = np.append(X_position,  np.load("../../data_simulated/npy/X_positions.npy").astype(np.int8), axis=0)
    y_moves = np.load("../../data/npy/y_moves.npy").astype(np.uint8) 
    y_moves = np.append(y_moves,  np.load("../../data_simulated/npy/y_moves.npy").astype(np.uint8), axis=0)
    y_result = np.load("../../data/npy/y_result.npy").astype(np.int8)
    y_result = np.append(y_result,  np.load("../../data_simulated/npy/y_result.npy").astype(np.int8), axis=0)
    X_white_move = np.load("../../data/npy/X_white_move.npy").astype(np.int8)
    X_white_move = np.append(X_white_move,  np.load("../../data_simulated/npy/X_white_move.npy").astype(np.int8), axis=0)
    X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,\
                y_moves_train, y_moves_test, y_result_train, y_result_test = train_test_split(
                                            X_position, X_white_move, y_moves, y_result,
                                            test_size=0.1, random_state=42)

    # print('Train and test set shapes')
    print(X_position.shape)
    # print(X_pos_test.shape)
    # print(y_scr_train.shape)
    # print(y_scr_test.shape)

    tfjs_target_dir = "../../saved_model_js_1"
    for i in tqdm(range(1, 21)):
        model = create_model(num_convolutions=i)

        model = train(model, X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,
                    y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir,
                    tensorboard_dir="./logs_"+str(i)+"_convolutions")

        model.save(f'model_convolutions_{i}')
