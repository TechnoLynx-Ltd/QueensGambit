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


def approx_pos_score(result, move_idx, move_count):
    """
    Approximate a board score based on game progress and final result
    :param result:
    :param move_idx:
    :param move_count:
    :return: pos_score: np.ndarry -
    """
    assert result in ['1-0', '0-1', '1/2-1/2']
    assert move_idx <= move_count

    # Result is a binary exclusive class
    pos_score = np.zeros((2,), dtype=float)

    # Weight is in exponential relation with game's move progress: float from 0 to 1
    # Factor can go up to 1000 or even more, check link:
    # https://www.wolframalpha.com/input/?i=%281000%5Ex+-+1%29+%2F+%281000+-+1%29+from+0+to+1
    factor = 10
    weight = (factor ** (move_idx / move_count) - 1) / (factor - 1)
    assert 0 <= weight <= 1

    if result == '1-0':
        # White wins
        pos_score[0] = .5 + (.5 * weight)
    elif result == '0-1':
        # Black wins
        pos_score[0] = .5 - (.5 * weight)
    else:
        # Draw
        pos_score[0] = .5

    # Black's approximate score
    pos_score[1] = 1 - pos_score[0]

    return pos_score


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
                piece_positions[i, j, position_dict[pos]] = 1

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
        scores = []
        moves = []

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
            for move_idx, move in enumerate(game.mainline_moves()):
                board.push(move)
                piece_positions = parse_board(board)

                # Calculate no. moves left
                moves_left = move_count - (move_idx + 1)

                # Save positions
                positions.append(piece_positions)

                # Approximate and save current position's score
                scores.append(approx_pos_score(result, move_idx, move_count))

                # Save no. moves left until end of game
                moves.append(moves_left)

    # Convert extracted data into ndarray
    positions = np.array(positions)
    scores = np.array(scores)
    moves = np.array(moves).astype(np.uint8)

    assert 0 <= scores.min()
    assert scores.max() <= 1

    # Info
    print(f'File {filename} parsed')
    print(f'Positions: {positions.shape}')
    print(f'Scores: {scores.shape}')
    print(f'Moves: {moves.shape}')

    return positions, scores, moves


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
    y_score = np.empty((0, 2))
    y_moves = np.empty((0,))

    for filename in filenames:
        # Parse .pgn file
        positions, scores, moves = parse_pgn(filename, debug)

        # Build dataset
        X_position = np.append(X_position, positions, axis=0)
        y_score = np.append(y_score, scores, axis=0)
        y_moves = np.append(y_moves, moves, axis=0)

    if save_to_file:
        print("Saving dataset to file")
        with open("../../data/npy/X_positions.npy", 'wb') as X_pos_file:
            np.save(X_pos_file, X_position)
        with open("../../data/npy/y_scores.npy", "wb") as y_scr_file:
            np.save(y_scr_file, y_score)
        with open("../../data/npy/y_moves.npy", "wb") as y_res_file:
            np.save(y_res_file, y_moves)

    return X_position, y_score, y_moves


if __name__ == '__main__':
    from os import listdir
    from os.path import isfile, join

    path = '../../data/pgn/'

    filenames = [path + f for f in listdir(path) if isfile(join(path, f))]

    load_data_from_pgn(filenames, save_to_file=True, debug=False)

    print('Open and check .npy files')
    print(np.load("../../data/npy/X_positions.npy").shape)
    print(np.load("../../data/npy/y_moves.npy").shape)
    print(np.load("../../data/npy/y_scores.npy").shape)
