import chess.pgn
import numpy as np
import json
from numpy import savetxt

"""
Result tag:
1-0: white wins
0-1: black wins
1/2-1/2: draw
*: game still in progress, game abandoned, result unknown
"""

class DataParser:

    def __init__(self):
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
        piece_positions = np.zeros((8, 8, 12))

        lines = board_string.split("\n")
        for i, line in enumerate(lines):
            positions = line.split(" ")
            for j, pos in enumerate(positions):
                if pos != ".":
                    piece_positions[i, j, self.position_dict[pos]] = 1

        return piece_positions

    def parse_pgn(self, fname, limit = 1):
        pgn = open(fname)
        i = 0
        eof = False



        while not eof and i < limit:
            cur_game = chess.pgn.read_game(pgn)
            cur_board = cur_game.board()
            move_idx = 1
            move_count = cur_game.end().ply()
            result = cur_game.__str__().split(" ")[-1]
            ## Todo: do I add the starting board to the data?
            for move in cur_game.mainline_moves():
                cur_board.push(move)
                board_string = cur_board.__str__()
                moves_left = move_count - move_idx
                piece_positions = self.parse_board(board_string)
                move_idx += 1

                with open("input.json", "w") as write_file:
                    json.dump(piece_positions.tolist(), write_file)

            if cur_game == None:
                eof = True
            i += 1




"""
A structure to hold:
board state (8x8x12 array)
moves remaining until the end of the game
result of the game

example to get white pawns: print(bstate[:,:,0])
"""
class BoardState:
    def __init__(self, board, moves_to_win, result):
        self.board = board
        self.moves_to_win = moves_to_win
        self.result = result

