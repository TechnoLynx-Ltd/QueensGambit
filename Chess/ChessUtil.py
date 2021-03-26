import chess.pgn
import numpy as np
import h5py

"""
Result tag:
1-0: white wins
0-1: black wins
1/2-1/2: draw
*: game still in progress, game abandoned, result unknown
"""

"""
A structure to hold:
board state (8x8x12 array)
moves remaining until the end of the game
result of the game

example to get white pawns: print(bstate[:,:,0])
"""
class DataParser:

    def __init__(self):
        self.piece_pos_shape = (8, 8, 12,)
        self.position_dict = {
            'P': 0,
            'R': 1,
            'N': 2,
            'B': 3,
            'Q': 4,
            'K': 5,
            'p': 6,
            'r': 7,
            'n': 8,
            'b': 9,
            'q': 10,
            'k': 11

        }

    def parse_result(self, result):
        if result == "1/2-1/2":
            return 0
        if result[0] == "0":
            return -1
        if result[0] == "1":
            return 1
        return 0


    def parse_board(self, board_string):
        piece_positions = np.zeros(self.piece_pos_shape)
        lines = board_string.split("\n")
        for i, line in enumerate(lines):
            positions = line.split(" ")
            for j, pos in enumerate(positions):
                if pos != ".":
                    piece_positions[i, j, self.position_dict[pos]] = 1

        return piece_positions

    def parse_pgn(self, fname, limit=100, save_to_file=False):
        pgn = open(fname)
        i = 0
        eof = False
        inputs = []
        results = []
        moves = []

        while not eof and i < limit:
            cur_game = chess.pgn.read_game(pgn)
            cur_board = cur_game.board()
            move_idx = 1
            move_count = cur_game.end().ply()
            result = cur_game.__str__().split(" ")[-1]
            for move in cur_game.mainline_moves():
                cur_board.push(move)
                board_string = cur_board.__str__()
                moves_left = move_count - move_idx
                piece_positions = self.parse_board(board_string)

                inputs.append(piece_positions)
                results.append(result)
                moves.append(moves_left)

                move_idx += 1
            if cur_game == None:
                eof = True
            i += 1

        if save_to_file:
            print("Saving inputs and targets to file...")
            with open("input.npy", 'wb') as input_file:
                np.save(input_file, np.stack(inputs, axis=0))
            with open("target.npy", "wb") as target_file:
                np.save(target_file, np.stack(results, axis=0))
            with open("moves_left.npy", "wb") as moves_left_file:
                np.save(moves_left_file, np.stack(moves, axis=0))

        return inputs, results, moves

    def load_data_from_file(self):
        inputs = np.load("input.npy")
        results = np.load("target.npy")
        moves = np.load("moves_left.npy")
        return inputs, results, moves


    def file_test(self):
        # inputs, results, moves = self.parse_pgn("ficsgamesdb_202001_chess2000_nomovetimes_195915.pgn")
        inputs = np.load("input.npy")
        results = np.load("target.npy")
        moves = np.load("moves_left.npy")
        print(len(inputs))
        print(len(results))
        print(len(moves))
        print(inputs[0][:, :, 0])
        print(moves[0])
        inputs = np.stack(inputs, axis=0)
        results = np.stack(results, axis=0)
        moves = np.stack(moves, axis=0)
        print(inputs.shape)
        print(inputs[0,:,:,0])

        print(results.shape)
        # print(inputs[0, :, :, 0])

        print(moves.shape)
        # print(inputs[0, :, :, 0])


