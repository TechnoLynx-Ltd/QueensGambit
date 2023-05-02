import numpy as np
from sklearn.model_selection import train_test_split
# import tensorflowjs as tfjs
from model import create_model
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
import tensorflow as tf
import os
import shutil
from tqdm import tqdm
import pandas as pd
from tensorflow.keras.utils import Sequence
import chess


def bitboards_to_array(bb: np.ndarray) -> np.ndarray:
    bb = np.asarray(bb, dtype=np.uint64)[:, np.newaxis]
    s = 8 * np.arange(7, -1, -1, dtype=np.uint64)
    b = (bb >> s).astype(np.uint8)
    b = np.unpackbits(b, bitorder="little")
    return b.reshape(-1, 8, 8)

def array_from_fen(fen:str):
    board = chess.Board(fen=fen)

    black, white = board.occupied_co

    bitboards = np.array([
        white & board.pawns,
        white & board.rooks,
        white & board.knights,
        white & board.bishops,
        white & board.queens,
        white & board.kings,
        black & board.pawns,
        black & board.rooks,
        black & board.knights,
        black & board.bishops,
        black & board.queens,
        black & board.kings,
    ], dtype=np.uint64)

    return bitboards_to_array(bitboards)

def scheduler(epoch, lr):
  if epoch < 10:
    return lr
  else:
    return lr * tf.math.exp(-0.1)


def train(model, X_all_train, X_all_test, X_white_move_train, X_white_move_test,
                y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir,
                tensorboard_dir = "./logs"):
    try:
        os.mkdir(tensorboard_dir)
    except OSError as error:
        shutil.rmtree(tensorboard_dir)
        os.mkdir(tensorboard_dir)
    tensorboard_callback = TensorBoard(log_dir=tensorboard_dir, histogram_freq=1, profile_batch=3)
    lr_callback = tf.keras.callbacks.LearningRateScheduler(scheduler)
    checkpoint = ModelCheckpoint(tensorboard_dir+'_checkpoint', monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    train_gen = DataGenerator(X_all_train[:500000], X_white_move_train[:500000], y_moves_train[:500000], y_result_train[:500000], from_fen =True)
    test_gen = DataGenerator(X_all_test, X_white_move_test, y_moves_test, y_result_test)

    with tf.device('/gpu:0'):
        history = model.fit(
           train_gen,
            epochs=50,
            batch_size=32,
            validation_data=test_gen,
            shuffle=True,
            callbacks = [tensorboard_callback, lr_callback, checkpoint]
            )

    print(history.history)
    # tfjs.converters.save_keras_model(model, tfjs_target_dir)
    return model
   

class DataGenerator(Sequence):
    def __init__(self, x_position, x_white_move, y_moves, y_result, from_fen=False, batch_size=16):
        self.x_position,self.x_white_move, self.y_moves, self.y_result= x_position, x_white_move, y_moves, y_result
        self.batch_size = batch_size
        self.from_fen = from_fen

    def __len__(self):
        return int(np.ceil(len(self.x_position) / float(self.batch_size)))

    def __getitem__(self, idx):
        X_position = None
        if self.from_fen:
            positions = []
            for fen_pos in self.x_position[idx * self.batch_size:(idx + 1) * self.batch_size]:
                positions.append(array_from_fen(fen_pos))
            X_position = np.array(positions)
            X_position = X_position.reshape((X_position.shape[0],8, 8, 12))
        else:
            X_position = self.x_position[idx * self.batch_size:(idx + 1) * self.batch_size] 
        white_move = []
        for record in self.x_white_move[idx * self.batch_size:(idx + 1) * self.batch_size]:
            white_move.append([[[record]] * 8] *8)
        X_white_move = np.array(white_move)
        X_all = np.append(X_position, X_white_move, axis=3)

        batch_x = X_all
        batch_y_result = self.y_result[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y_moves = self.y_moves[idx * self.batch_size:(idx + 1) * self.batch_size]
        return ({"board": batch_x},
            {"winner": batch_y_result, "moves_left": batch_y_moves, "winner_first": batch_y_result, "winner_second":batch_y_result})
           

if __name__ == '__main__':
    X_position_val = np.load("../../data/npy/X_positions.npy").astype(np.int8)
    X_white_move_val = np.load("../../data/npy/X_white_move.npy").astype(np.uint8)
    y_moves_val = np.load("../../data/npy/y_moves.npy")
    y_result_val = np.load("../../data/npy/y_result.npy")

    y_moves = np.load("../../data_sim_bitboard_real_game/npy/y_moves.npy").astype(np.uint8)
    indeces = (y_moves<=50)
    y_moves = y_moves[indeces]
    y_result = np.load("../../data_sim_bitboard_real_game/npy/y_result.npy").astype(np.int8)
    y_result = y_result[indeces]
    X_white_move = np.load("../../data_sim_bitboard_real_game/npy/X_white_move.npy").astype(np.int8)
    X_white_move = X_white_move[indeces]
    X_position_simulated = np.load("../../data_sim_bitboard_real_game/npy/fen_bitboards.npy")
    # X_position_simulated= X_position_simulated.reshape((X_position_simulated.shape[0],8, 8, 12))
    X_position = X_position_simulated[indeces]
    # white_move = []
    # for record in X_white_move:
    #     white_move.append([[[record]] * 8] *8)
    # X_white_move = np.array(white_move)
    # X_all = np.append(X_position, X_white_move, axis=3)

    # X_position = np.append(X_position,  X_position_simulated, axis=0)
    # X_position = np.append(X_position,  np.load("../../data_unused/npy/X_positions.npy").astype(np.int8), axis=0)
    # y_moves = np.append(y_moves,  np.load("../../data_sim_bitboard/npy/y_moves.npy").astype(np.uint8), axis=0)
    # y_moves = np.append(y_moves,  np.load("../../data_unused/npy/y_moves.npy").astype(np.uint8), axis=0)
    # y_result = np.append(y_result,  np.load("../../data_sim_bitboard/npy/y_result.npy").astype(np.int8), axis=0)
    # y_result = np.append(y_result,  np.load("../../data_unused/npy/y_result.npy").astype(np.int8), axis=0)
    # X_white_move = np.append(X_white_move,  np.load("../../data_sim_bitboard/npy/X_white_move.npy").astype(np.int8), axis=0)
    # X_white_move = np.append(X_white_move,  np.load("../../data_unused/npy/X_white_move.npy").astype(np.int8), axis=0)
    # y_moves = y_moves[indeces]
    # df = pd.DataFrame(y_moves, columns=['moves'])
    # min_boards = min(df.groupby(['moves'])['moves'].count())
    # indeces = []
    # for i in range (51):
    #     df_moves = df[df['moves'] == i]
    #     indeces = indeces + list(df_moves.index.values[:min_boards])

    # print(X_all.shape, X_all[indeces].shape)

    # X_position_train,X_position_test, X_white_move_train, X_white_move_test,\
                # y_moves_train, y_moves_test, y_result_train, y_result_test = train_test_split(
                #                         X_position, X_white_move, y_moves, y_result, test_size=0.2, random_state=42)

    # print('Train and test set shapes')
    # print(X_position.shape)
    # print(X_pos_test.shape)
    # print(y_scr_train.shape)
    # print(y_scr_test.shape)

    tfjs_target_dir = "../../saved_model_js_1"
    model = create_model(num_convolutions_total=18, num_conv_in_block=3)
    # model = tf.keras.models.load_model('/home/otsepilova/QueensGambit/python/model/logs_model_10_sim_data_checkpoint')
    model = train(model, X_position, X_position_val, X_white_move, X_white_move_val, y_moves, y_moves_val, y_result,
                 y_result_val, tfjs_target_dir, tensorboard_dir="logs_model_sim_data_real_games_validation_real_games_fixed")
    model.save(f'model_sim_data_real_game_validation_real_games_fixed')
    # for i in tqdm(range(8, 21)):
    #     model = create_model(num_convolutions_total=i, num_conv_in_block=3)

    #     model = train(model, X_all_train, X_all_test,
    #                 y_moves_train, y_moves_test, y_result_train, y_result_test, tfjs_target_dir,
    #                 tensorboard_dir="./logs_"+str(i)+"_convolutions_l1")

    #     model.save(f'model_convolutions_{i}_l1')
