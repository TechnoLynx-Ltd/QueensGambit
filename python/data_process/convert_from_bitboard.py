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

if __name__ == "__main__":
    fen_position = np.load("../../data_sim_bitboard/npy/fen_bitboards.npy")
    positions = []
    for fen_pos in tqdm(fen_position):
        positions.append(array_from_fen(fen_pos))
    X_position = np.array(positions)
    with open(f"../../data_sim_bitboard/npy/X_positions.npy", 'wb') as X_pos_file:
        np.save(X_pos_file, X_position)
