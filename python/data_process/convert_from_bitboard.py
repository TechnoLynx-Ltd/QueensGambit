import chess
import numpy as np
from tqdm import tqdm

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
def to_categorical(board):
    print(board)
    board_categorical = np.zeros((8,8,12))
    for i in range(8):
        for j in range(8):
            for k in range(12):
                if board[k][i][j] !=0:
                    board_categorical[i][j][k] = 1
    return board_categorical

if __name__ == "__main__":
    fen_position = np.load("../../data_sim_bitboard_real_game/npy/fen_bitboards.npy")[:1]
    positions = []
    for fen_pos in tqdm(fen_position):
        print(fen_pos)
        print(array_from_fen(fen_pos)[0])
        positions.append(to_categorical(array_from_fen(fen_pos)))
    X_position = np.array(positions)
    # X_position = X_position.reshape((X_position.shape[0],8, 8, 12))
    position_dict = {'wP': 0, 'wR': 1, 'wN': 2, 'wB': 3, 'wQ': 4, 'wK': 5,
                              'bP': 6, 'bR': 7, 'bN': 8, 'bB': 9, 'bQ': 10, 'bK': 11}
    position_dict = {v: k for k, v in position_dict.items()}
    for idx, board in enumerate(X_position):
        print(fen_position[idx])
        fen_str = ''
        count_empty = 0
        print(board[0])
        for i in range(8): 
            for j in range(8):
                board_piece = '--'
                for k in range(12):
                    if board[i][j][k] == 1:
                        board_piece = position_dict[k]
                        # print(i,j,k)

                if board_piece == '--':
                    count_empty += 1
                    if j == 7:
                        fen_str += str(count_empty)
                        count_empty = 0
                else:
                    if count_empty != 0:
                        fen_str += str(count_empty)
                        count_empty = 0
                    
                    symb = board_piece[1]
                    if board_piece[0] == 'b':
                        symb = symb.lower()
                    
                    fen_str += symb
            if i != 7:
                fen_str += '/'
            else: 
                fen_str += ' '
        
        # #who makes move
        # if X_white_to_move[idx] == 1:
        #     fen_str += 'w '
        # else:
        #     fen_str += 'b '
        
        print(fen_str)
        # print(y_result[idx])
        break
