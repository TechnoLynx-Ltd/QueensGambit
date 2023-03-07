# import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflowjs as tfjs
from model import create_model
from tensorflow.keras.callbacks import TensorBoard
import tensorflow as tf
import os
# os.environ['CUDA_VISIBLE_DEVICES'] = "0"


def averaging_validation(X_pos_test, X_white_move_test, y_moves_test, y_result_test):
    # merged_with_moves = np.column_stack((X_pos_test, X_white_move_test))
    # print(merged_with_moves)
    X_pos= np.empty((0, 8, 8))
    y_moves = np.empty((0,))
    y_result = np.empty((0,3))
    X_white_move = np.empty((0,))
    indices = np.arange(X_pos_test.shape[0])
    while len(indices) > 0:
        if(len(indices)%100==0):
            print(len(indices))
        cur_board_idx = indices[0]
        all_similar = [cur_board_idx]
        results = list(map(int, y_result_test[cur_board_idx]))
        moves = int(y_moves_test[cur_board_idx])
        for other_board_idx in indices[1:]:
            if X_white_move_test[other_board_idx] == X_white_move_test[cur_board_idx] and np.all(X_pos_test[other_board_idx] == X_pos_test[cur_board_idx]):
                moves += y_moves_test[other_board_idx]
                results[0] += y_result_test[other_board_idx][0]
                results[1] += y_result_test[other_board_idx][1]
                results[2] += y_result_test[other_board_idx][2]
                # y_result_test[other_board_idx][1], y_result_test[other_board_idx][2]
                results.append(y_result_test[other_board_idx])
                all_similar.append(other_board_idx)
        X_pos = np.append(X_pos, np.array([X_pos_test[cur_board_idx]]), axis=0)
        X_white_move = np.append(X_white_move, np.array([X_white_move_test[cur_board_idx]]), axis=0)
        y_moves = np.append(y_moves, np.array([moves/len(all_similar)]), axis=0)
        y_result = np.append(y_result, np.array([(results[0]/len(all_similar), results[1]/len(all_similar), results[2]/len(all_similar))]), axis=0)
        indices = [x for x in indices if x not in  all_similar]
    return X_pos, X_white_move, y_moves, y_result




def train(model, X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,
                y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir):

    tensorboard_callback = TensorBoard(log_dir='./logs1', histogram_freq=1)
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
    # X_position = np.append(X_position,  np.load("../../simulated_data_1/npy/X_positions.npy").astype(np.int8), axis=0)
    y_moves = np.load("../../data/npy/y_moves.npy").astype(np.int8)
    # y_moves = np.append(y_moves,  np.load("../../simulated_data_1/npy/y_moves.npy").astype(np.int8), axis=0)
    y_result = np.load("../../data/npy/y_result.npy").astype(np.int8)
    # y_result = np.append(y_result,  np.load("../../simulated_data_1/npy/y_result.npy").astype(np.int8), axis=0)
    X_white_move = np.load("../../data/npy/X_white_move.npy").astype(np.int8)
    # X_white_move = np.append(X_white_move,  np.load("../../simulated_data_1/npy/X_white_move.npy").astype(np.int8), axis=0)
    X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,\
                y_moves_train, y_moves_test, y_result_train, y_result_test = train_test_split(
                                            X_position, X_white_move, y_moves, y_result,
                                            test_size=0.1, random_state=42)
    X_pos_test, X_white_move_test, y_moves_test, y_result_test =  averaging_validation(X_pos_test, X_white_move_test, y_moves_test, y_result_test)
    print('Train and test set shapes')
    # print(X_pos_train.shape)
    # print(X_pos_test.shape)
    # print(y_scr_train.shape)
    # print(y_scr_test.shape)

    tfjs_target_dir = "../../saved_model_js_1"

    model = create_model()

    model = train(model, X_pos_train, X_pos_test, X_white_move_train, X_white_move_test,
                y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir)

    model.save('')
