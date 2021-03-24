import random

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


def find_minmax_best_move(gs, valid_moves):
    global next_move
    next_move = None
    find_minmax_move(gs, valid_moves, DEPTH, gs.white_to_move, -CHECKMATE, CHECKMATE)
    return next_move

def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_weights[square[1]]
            else:
                score -= piece_weights[square[1]]

    return score

"""
Positive score -> white
Negative score -> black
"""
def score_board(gs):
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

