import numpy as np
import matplotlib.pyplot as plt
def moves_left_stats(npy_folders):
    y_moves = np.empty((0,))
    for npy_folder in npy_folders:
        y_moves = np.append(y_moves,  np.load(f"{npy_folder}/y_moves.npy").astype(np.uint8), axis=0)
    counts, bins = np.histogram(y_moves)
    plt.stairs(counts, bins)
    plt.savefig('moves_stats.png')

if __name__ == "__main__":
    npy_folders = ["../../data/npy", "../../data_simulated/npy"]
    moves_left_stats(npy_folders)