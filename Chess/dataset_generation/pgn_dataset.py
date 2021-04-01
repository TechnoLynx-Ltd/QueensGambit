import chess.pgn
import numpy as np
import h5py

"""
Result tag:
1-0: white wins
0-1: black wins
1/2-1/2: draw
*: game still in progress, game abandoned, result unknown

A structure to hold:
board state (8x8x12 array)
moves remaining until the end of the game
result of the game
"""

all_ending_reasons = {'White forfeits on time',
                      'White forfeits by disconnection',
                      'Black checkmated',
                      'Black forfeits on time',
                      'Game drawn by repetition',
                      'Game drawn by mutual agreement',
                      'White wins by adjudication',
                      'Black wins by adjudication',
                      'Black forfeits by disconnection',
                      'Game drawn by stalemate',
                      'White checkmated',
                      'Neither player has mating material',
                      'Game drawn because both players ran out of time',
                      'White resigns',
                      'White ran out of time and Black has no material to mate',
                      'Game drawn by the 50 move rule',
                      'Black resigns',
                      'Black ran out of time and White has no material to mate'}

position_dict = {'P': 0, 'R': 1, 'N': 2, 'B': 3, 'Q': 4, 'K': 5,
                 'p': 6, 'r': 7, 'n': 8, 'b': 9, 'q': 10, 'k': 11}


def parse_result(game):
    """
    Reads result of Game object and converts into dual category
    :param game: chess.pgn.Game
    :return result: np.ndarry
    """
    assert type(game) is chess.pgn.Game

    # Game object in string format
    game_str = str(game)

    # Find reason of game ending
    start = game_str.rfind('{')
    end = game_str.rfind('}')
    end_reason = game_str[start + 1: end].strip()

    # If ending reason is not due to game performance return None
    non_performance_ending_reasons = {'White forfeits on time',
                                      'Black forfeits on time',
                                      'White wins by adjudication',
                                      'Black wins by adjudication',
                                      'White forfeits by disconnection',
                                      'Black forfeits by disconnection',
                                      'Game drawn because both players ran out of time',
                                      'White ran out of time and Black has no material to mate',
                                      'Black ran out of time and White has no material to mate'}

    if end_reason in non_performance_ending_reasons:
        return None

    # Result is a dual category label
    result = np.zeros((2,), dtype=np.int8)

    # Result in game info
    if '[Result "1-0"]' in game_str:
        # White wins
        result[0] = 1
        result_info = "1-0"
    elif '[Result "0-1"]' in game_str:
        # Black wins
        result_info = "0-1"
        result[1] = 1
    elif '[Result "1/2-1/2"]' in game_str:
        # Draw
        result_info = "1/2-1/2"
    else:
        raise Exception(f'Unknown result in game info: \n {game_str}')

    # Result at end of moves list
    result_end = game_str.split(" ")[-1]

    # Info redundancy check
    assert result_end == result_info

    return result


def parse_board(board):
    """
    Parse Board object to ndarray of size 8x8x12
    :param board: chess.Board
    :return piece_positions: np.ndarray
    """
    assert type(board) is chess.Board

    piece_positions = np.zeros((8, 8, 12), dtype=np.int8)

    lines = str(board).split("\n")
    for i, line in enumerate(lines):
        positions = line.split(" ")
        for j, pos in enumerate(positions):
            if pos != ".":
                piece_positions[i, j, position_dict[pos]] = 1

    return piece_positions


def parse_pgn(filename, limit=100, save_to_file=False):
    with open(filename, 'r') as pgn:

        # Dataset is built by appending to lists b/c it is faster than appending to np.ndarrays
        inputs = []
        results = []
        moves = []

        loop_count = 0
        while loop_count < limit:
            print(loop_count)
            loop_count += 1

            # Parse .pgn file to Game object
            game = chess.pgn.read_game(pgn)

            # Stop parsing at the end of .pgn file
            if game is None:
                break

            board = game.board()
            move_count = game.end().ply()

            # Parse result
            result = parse_result(game)

            # Move to next game if result is not acceptable
            if result is None:
                continue

            # Parse moves
            for move_idx, move in enumerate(game.mainline_moves()):
                board.push(move)
                piece_positions = parse_board(board)

                moves_left = move_count - (move_idx + 1)

                # Build dataset
                inputs.append(piece_positions)
                results.append(result)
                moves.append(moves_left)

    # Convert extracted data
    inputs = np.array(inputs)
    print(inputs.shape)
    results = np.array(results)
    print(results.shape)
    moves = np.array(moves)
    print(moves.shape)

    if save_to_file:
        print("Saving inputs and targets to file...")
        with open("input.npy", 'wb') as input_file:
            np.save(input_file, np.stack(inputs, axis=0))
        with open("target.npy", "wb") as target_file:
            np.save(target_file, np.stack(results, axis=0))
        with open("moves_left.npy", "wb") as moves_left_file:
            np.save(moves_left_file, np.stack(moves, axis=0))

    return inputs, results, moves


def load_data_from_file():
    inputs = np.load("input.npy")
    results = np.load("target.npy")
    moves = np.load("moves_left.npy")
    return inputs, results, moves


def file_test():
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
    print(inputs[0, :, :, 0])

    print(results.shape)
    # print(inputs[0, :, :, 0])

    print(moves.shape)
    # print(inputs[0, :, :, 0])


if __name__ == '__main__':
    inputs_, results_, moves_ = parse_pgn('../data/ficsgamesdb_202101_standard2000_nomovetimes_197232.pgn')
