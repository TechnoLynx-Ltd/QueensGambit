import numpy as np

if __name__ == "__main__":
    X_position_val = np.load("../../data/npy/X_positions.npy").astype(np.int8)
    y_moves = np.load("../../data/npy/y_moves.npy").astype(np.uint8)
    indeces = (y_moves==1)
    y_result = np.load("../../data/npy/y_result.npy").astype(np.int8)
    X_white_to_move = np.load("../../data/npy/X_white_move.npy").astype(np.int8)
    y_result = y_result[indeces]
    X_white_to_move = X_white_to_move[indeces]
    X_position_val = X_position_val[indeces]
    position_dict = {'wP': 0, 'wR': 1, 'wN': 2, 'wB': 3, 'wQ': 4, 'wK': 5,
                              'bP': 6, 'bR': 7, 'bN': 8, 'bB': 9, 'bQ': 10, 'bK': 11}
    position_dict = {v: k for k, v in position_dict.items()}
    for idx, board in enumerate(X_position_val):
        fen_str = ''
        count_empty = 0
        for i in range(8):
            for j in range(8):
                board_piece = '--'
                for k in range(12):
                    if board[i][j][k] == 1:
                        board_piece = position_dict[k]
                        print(i,j,k)

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
        
        #who makes move
        if X_white_to_move[idx] == 1:
            fen_str += 'w '
        else:
            fen_str += 'b '
        
        print(fen_str)
        print(y_result[idx])
        break
    