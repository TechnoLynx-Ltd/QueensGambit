const piece_weights =
{
    '-': 0,
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 10,
    'K': 0
};

const checkmate = 1000;
const stalemate = 0;
const max_depth = 3;

function find_random_move(valid_moves)
{
    return valid_moves[Math.floor(Math.random() * valid_moves.length)];
}

function find_greedy_move(game_state, valid_moves, is_ai_white)
{
    const turn_weight = (game_state.white_to_move == is_ai_white) ? 1 : -1;
    let max_score = -checkmate;
    let best_move = null;
    let score;

    for (const player_move of valid_moves)
    {
        game_state.make_move(player_move);

        if (game_state.checkmate)
        {
            score = checkmate * turn_weight;
        }
        else if (game_state.stalemate)
        {
            score = 0;
        }
        else
        {
            score = score_material(game_state.board, is_ai_white) * turn_weight;
        }

        if (score > max_score)
        {
            max_score = score;
            best_move = player_move;
        }

        game_state.undo_move();
    }

    return best_move;
}

function find_minmax_best_move(game_state, valid_moves)
{
    const next_move_result =
        find_minmax_move(
            game_state,
            valid_moves,
            max_depth,
            game_state.white_to_move,
            -checkmate,
            checkmate);

    return next_move_result.move;
}

function find_minmax_move(
    game_state, valid_moves, depth, is_ai_white, alpha, beta)
{
    let next_move = null;

    if (depth == 0)
    {
        return { score: score_board(game_state, is_ai_white), move: next_move };
    }

    if (game_state.white_to_move == is_ai_white)
    {
        let max_score = -checkmate;

        for (const move of valid_moves)
        {
            game_state.make_move(move);

            const next_moves = game_state.get_valid_moves();
            const next_move_result =
                find_minmax_move(
                    game_state,
                    next_moves,
                    depth - 1,
                    is_ai_white,
                    alpha,
                    beta);

            if (next_move_result.score > max_score)
            {
                max_score = next_move_result.score;
                next_move = move;
            }

            alpha = Math.max(next_move_result.score, alpha);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }

        return { score: max_score, move: next_move };
    }
    else
    {
        let min_score = checkmate;

        for (const move of valid_moves)
        {
            game_state.make_move(move);

            const next_moves = game_state.get_valid_moves();
            const next_move_result =
                find_minmax_move(
                    game_state,
                    next_moves,
                    depth - 1,
                    is_ai_white,
                    alpha,
                    beta);

            if (next_move_result.score < min_score)
            {
                min_score = next_move_result.score;
                next_move = move;
            }

            beta = Math.min(next_move_result.score, beta);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }

        return { score: min_score, move: next_move };
    }
}

function score_material(board, is_ai_white)
{
    let score = 0;

    for (const row of board)
    {
        for (const square of row)
        {
            const is_piece_white = (square[0] == "w");
            const weight = (is_ai_white == is_piece_white) ? 1 : -1;

            score += weight * piece_weights[square[1]];
        }
    }

    return score;
}

function score_board(game_state, is_ai_white)
{
    const weight = (game_state.white_to_move == is_ai_white) ? 1 : -1;

    if (game_state.checkmate)
    {
        return checkmate * -weight;
    }
    else if (game_state.stalemate)
    {
        return stalemate;
    }

    return score_material(game_state.board, is_ai_white);
}