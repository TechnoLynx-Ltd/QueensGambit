"""
Module of AI invoking methods
"""

import random
import numpy as np

piece_weights = {
    '-': 0,
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 10,
    'K': 0
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def find_rand_move(valid_moves):
    chosen_move = random.choice(valid_moves)
    return chosen_move


def find_greedy_move(gs, valid_moves):
    turn_mult = 1 if gs.white_to_move else -1
    max_score = -CHECKMATE
    best_move = None

    for player_move in valid_moves:
        gs.make_move(player_move)
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = 0
        else:
            score = score_material(gs.board) * turn_mult
        if score > max_score:
            max_score = score
            best_move = player_move
        gs.undo_move()
    return best_move


def find_minmax_best_move(gs, valid_moves):
    global next_move
    next_move = valid_moves[0]
    find_minmax_move(gs, valid_moves, DEPTH, gs.white_to_move, -CHECKMATE, CHECKMATE)
    return next_move


def find_minmax_move(gs, valid_moves, depth, white_to_move, alpha, beta):
    global next_move
    if depth == 0:
        return score_board(gs)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_minmax_move(gs, next_moves, depth - 1, False, alpha, beta)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
            if score > alpha:
                alpha = score
            if beta <= alpha:
                break
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_minmax_move(gs, next_moves, depth - 1, True, alpha, beta)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
            if score < beta:
                beta = score
            if beta <= alpha:
                break
        return min_score


def find_model_best_move(game_state, valid_moves, model):
    """
    Predict the score of all valid moves with a trained model and return the move with the highest score
    :param game_state: GameState
    :param valid_moves: list of Move
    :param model: keras.model
    :return: Move
    """
    max_score = 0
    for move in valid_moves:

        # Make a valid move
        game_state.make_move(move)

        # Expand current position to 4D b/c model input requirement
        nested_list_pos = game_state.get_position()
        nested_list_pos = [[[[nested_list_pos[i][j][k] for k in range(12)] for j in range(8)] for i in range(8)]
                           for n in range(1)]  # numpy alternative

        # Model predicts score (shape:(1,2)) of current position
        score = model.predict(nested_list_pos)
        assert score[0, 0] + score[0, 1] >= 0.99

        if game_state.white_to_move:  # White moves
            # White score
            score = score[0, 0]
        else:  # Black moves
            # Black score
            score = score[0, 1]

        if score > max_score:
            max_score = score
            next_move = move

        # Restore game_state into original position
        game_state.undo_move()

    return next_move

def find_model_best_move_without_scoring(game_state, valid_moves, model):
    min_loosing = (0,0,float("inf"))
    cur_left_to_win = float("inf")
    for move in valid_moves:

        # Make a valid move
        game_state.make_move(move)

        # Expand current position to 4D b/c model input requirement
        nested_list_pos = game_state.get_position()
        nested_list_pos = [[[[nested_list_pos[i][j][k] for k in range(12)] for j in range(8)] for i in range(8)]
                           for n in range(1)]  # numpy alternative

        # Model predicts score (shape:(1,2)) of current position
        # res = np.asarray(nested_list_pos).astype(np.uint8)
        prediction = model.predict([np.asarray(nested_list_pos).astype(np.uint8), np.asarray([game_state.white_to_move]).astype(np.uint8)])
        move_result = prediction[0][0]
        left_to_win = prediction[1][0]
        if not game_state.white_to_move:
            move_result = tuple(move_result[::-1])
        
        if min_loosing[2] - move_result[2] > 0.05:
            min_loosing = move_result
            next_move = move
            cur_left_to_win = left_to_win
        elif min_loosing[2] - move_result[2] > -0.05:
            if min_loosing[2] - move_result[2] > 0.05:
                min_loosing = move_result
                next_move = move
                cur_left_to_win = left_to_win
            elif min_loosing[2] - move_result[2] > -0.05 and left_to_win < cur_left_to_win:
                min_loosing = move_result
                next_move = move
                cur_left_to_win = left_to_win

        # Restore game_state into original position
        game_state.undo_move()
    print(min_loosing, cur_left_to_win)
    return next_move

def score_material(board):
    """
    Positive score -> white
    Negative score -> black
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_weights[square[1]]
            else:
                score -= piece_weights[square[1]]

    return score


def score_board(gs):
    """
    Positive score -> white
    Negative score -> black
    """
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += piece_weights[square[1]]
            else:
                score -= piece_weights[square[1]]
    return score
