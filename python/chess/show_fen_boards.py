import numpy as np
if __name__ == "__main__":
    y_moves = np.load("../../data_sim_bitboard_less_random/npy/y_moves.npy").astype(np.uint8)
    indeces = (y_moves==1)
    X_position_simulated = np.load("../../data_sim_bitboard_less_random/npy/fen_bitboards.npy")
    X_position_simulated = X_position_simulated[indeces]
    y_result = np.load("../../data_sim_bitboard_less_random/npy/y_result.npy").astype(np.int8)
    y_result = y_result[indeces]
    i = 0
    black_won_indeces = set()
    white_won_indeces = set()
    stalemate_indeces = set()

    while i != len(X_position_simulated):
        if y_result[i][0] == 1:
            white_won_indeces.add(i)
        elif y_result[i][1] == 1:
            stalemate_indeces.add(i)
        else:
            black_won_indeces.add(i)
        i += 1
    
    print(f"White won {len(white_won_indeces)}")
    print(f'Stalemate won {len(stalemate_indeces)}')
    print(f'Black won {len(black_won_indeces)}')
    counter = 0
    for blac_won_indx in black_won_indeces:
        print(X_position_simulated[blac_won_indx])
        counter += 1
        if counter == 10:
            break
    