import chess.pgn
import h5py
import math
import numpy as np

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

non_performance_ending_reasons = {'White forfeits on time',
                                  'Black forfeits on time',
                                  'White wins by adjudication',
                                  'Black wins by adjudication',
                                  'White forfeits by disconnection',
                                  'Black forfeits by disconnection',
                                  'Game drawn because both players ran out of time',
                                  'White ran out of time and Black has no material to mate',
                                  'Black ran out of time and White has no material to mate'}

position_dict = {'P': 0, 'R': 1, 'N': 2, 'B': 3, 'Q': 4, 'K': 5,
                 'p': 6, 'r': 7, 'n': 8, 'b': 9, 'q': 10, 'k': 11}


def parse_result(game):
    """
    Reads result of Game object and converts into string of "1-0", "0-1" or "1/2-1/2"
    *: game still in progress, game abandoned, result unknown
    :param game: chess.pgn.Game
    :return result_info: str
    """
    assert type(game) is chess.pgn.Game

    # Game object into string format
    game_str = str(game)

    # Find reason of game ending
    start = game_str.rfind('{')
    end = game_str.rfind('}')
    end_reason = game_str[start + 1: end].strip()

    # If ending reason is not due to game performance return None
    if end_reason in non_performance_ending_reasons:
        return None

    # Result in game info
    if '[Result "1-0"]' in game_str:
        # White wins
        result_info = "1-0"
    elif '[Result "0-1"]' in game_str:
        # Black wins
        result_info = "0-1"
    elif '[Result "1/2-1/2"]' in game_str:
        # Draw
        result_info = "1/2-1/2"
    else:
        raise Exception(f'Unknown result in game info: \n {game_str}')

    # Result at end of moves list
    result_end = game_str.split(" ")[-1]

    # Info redundancy check
    assert result_end == result_info

    return result_info

def parse_board(board):
    """
    Parse Board object into ndarray of size (8, 8, 12)
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
                piece_positions[i, j] = position_dict[pos]+1

    return piece_positions


def parse_pgn(filename, debug=False):
    """
    Parse .pgn file
    :param filename:
    :param limit:
    :return:
    """
    with open(filename, 'r') as pgn:

        # Dataset is built by appending to lists b/c it is faster than appending to np.ndarrays
        positions = []
        moves = []
        results = []
        white_move = []


        if debug:
            limit = 10
        else:
            limit = 1000

        loop_count = 0

        while loop_count < limit:
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
            cur_white_move = True
            for move_idx, move in enumerate(game.mainline_moves()):
                board.push(move)
                piece_positions = parse_board(board)

                # Calculate no. moves left
                moves_left = move_count - (move_idx + 1)

                # Save positions
                positions.append(piece_positions)
                if result == "1-0":
                    results.append([1,0,0])
                elif result == "0-1":
                    results.append([0,0,1])
                else:
                    results.append([0,1,0])
                white_move.append(cur_white_move)
                cur_white_move = not cur_white_move


                # Save no. moves left until end of game
                moves.append(moves_left)

    # Convert extracted data into ndarray
    positions = np.array(positions)
    moves = np.array(moves).astype(np.uint8)
    results = np.array(results)
    white_move = np.array(white_move).astype(np.int8)

    # Info
    print(f'File {filename} parsed')
    print(f'Moves: {moves.shape}')
    print(f'Positions: {positions.shape}')
    print(f'Result: {results.shape}')
    print(f'White moves: {white_move.shape}')

    return positions, moves, results, white_move


def load_data_from_pgn(filenames, save_to_file=False, debug=False):
    """
    Load data from list of .pgn files and builds dataset
    :param filenames: list
    :param save_to_file: boolean
    :return: tuple of ndarrays - dataset
    """
    # Check if filenames is iterable
    try:
        iter(filenames)
    except TypeError as te:
        print(f'Argument filenames is not iterable')

    # Datasets accumulator
    X_position = np.empty((0, 8, 8, 12))
    y_moves = np.empty((0,))
    y_result = np.empty((0,3))
    X_white_move = np.empty((0,))

    for filename in filenames:
        # Parse .pgn file
        positions, moves, result, white_move = parse_pgn(filename, debug)

        # Build dataset
        X_position = np.append(X_position, positions, axis=0)
        y_moves = np.append(y_moves, moves, axis=0)
        y_result = np.append(y_result, result, axis=0)
        X_white_move = np.append(X_white_move, white_move, axis=0)

    if save_to_file:
        print("Saving dataset to file")
        with open("../../data/npy/X_positions.npy", 'wb') as X_pos_file:
            np.save(X_pos_file, X_position)
        with open("../../data/npy/X_white_move.npy", "wb") as y_res_file:
            np.save(y_res_file, X_white_move)
        with open("../../data/npy/y_moves.npy", "wb") as y_res_file:
            np.save(y_res_file, y_moves)
        with open("../../data/npy/y_result.npy", "wb") as y_res_file:
            np.save(y_res_file, y_result)

    return X_position, X_white_move, y_moves, y_result


if __name__ == '__main__':
    from os import listdir
    from os.path import isfile, join

    path = '../../data/pgn/'

    filenames = [path + f for f in listdir(path) if isfile(join(path, f))]

    load_data_from_pgn(filenames, save_to_file=True, debug=False)

    print('Open and check .npy files')
    print(np.load("../../data/npy/X_positions.npy").shape)
    print(np.load("../../data/npy/X_white_move.npy").shape)
    print(np.load("../../data/npy/y_moves.npy").shape)
    print(np.load("../../data/npy/y_result.npy").shape)
