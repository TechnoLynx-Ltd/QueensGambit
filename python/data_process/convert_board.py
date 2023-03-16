import numpy as np
from tqdm import tqdm

X_position = np.load("../../data_simulated/npy/X_positions.npy").astype(np.int8)
X_converted_positions = np.empty((0, 8, 8, 12))
for board in tqdm(X_position):
    nested_list_position = [[[0 for k in range(12)] for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            if board[i][j] != 0:
                nested_list_position[i][j][board[i][j]-1] = 1
    X_converted_positions = np.append(X_converted_positions, np.array([nested_list_position]), axis=0)
print(X_converted_positions.shape)
with open("../../data_simulated/npy/X_positions.npy", 'wb') as X_pos_file:
            np.save(X_pos_file, X_converted_positions)
