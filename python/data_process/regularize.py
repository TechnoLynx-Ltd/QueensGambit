import pandas as pd
import numpy as np

if __name__ == "__main__":
    y_moves = np.load("../../data_sim_bitboard/npy/y_moves.npy").astype(np.uint8)
    indeces = (y_moves<=50)
    y_moves = y_moves[indeces]
    df = pd.DataFrame(y_moves, columns=['moves'])
    min_boards = min(df.groupby(['moves'])['moves'].count())
    indeces = []
    for i in range (51):
        df_moves = df[df['moves'] == i]
        print(list(df_moves.index.values[:10]))
