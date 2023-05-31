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
const max_depth_minmax = 5;
const max_depth_sts = 3;
const GAME_DEPTH = 10;
const GAMES = 20;

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

export function find_minmax_best_move(game_state, valid_moves)
{
    const next_move_result =
        find_minmax_move(
            game_state,
            valid_moves,
            max_depth_minmax,
            game_state.white_to_move,
            -checkmate,
            checkmate);

    return next_move_result.move;
}


export default function weightedRandom(items, weights) {
 if (items.length !== weights.length) {
   throw new Error('Items and weights must be of the same size');
 }

 if (!items.length) {
   throw new Error('Items must not be empty');
 }

 const cumulativeWeights = [];
 cumulativeWeights[0] = weights[0];
 for (let i = 1; i < weights.length; i += 1) {
   cumulativeWeights[i] = weights[i] + cumulativeWeights[i - 1] ;
 }

 const maxCumulativeWeight = cumulativeWeights[cumulativeWeights.length - 1];
 const randomNumber = maxCumulativeWeight * Math.random();

 for (let itemIndex = 0; itemIndex < items.length; itemIndex += 1) {
   if (cumulativeWeights[itemIndex] >= randomNumber) {
     return items[itemIndex];
   }
 }
}

function compareNumbers(a, b) {
    return a - b;
  }

function find_minmax_move(
    game_state, valid_moves, depth, is_ai_white, alpha, beta)
{
    let next_move = null;

    if (depth == 0)
    {
        return { score: score_board(game_state, is_ai_white), move: next_move };
    }

    if(valid_moves.length == 0){
        return { score: score_board(game_state, is_ai_white), move: next_move };
    }

    //Shufflig so it would look more rational
    let shuffled_valid_moves = valid_moves.sort(function () {
        return Math.random() - 0.5;
      });
    
    let scores_moves = {};

    if (game_state.white_to_move)
    {
        let max_score = -checkmate - 1;

        for (const move of shuffled_valid_moves)
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

            if (next_move_result.score in scores_moves)
            {
               scores_moves[parseInt(next_move_result.score)].push(move)
            } else {
                scores_moves[parseInt(next_move_result.score)] = [move];
            }

            alpha = Math.max(next_move_result.score, alpha);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }
        let all_scores = Object.keys(scores_moves);
        if(all_scores.length == 0){
            return { score: -checkmate, move: next_move};
        }
        all_scores = all_scores.map(function(item) {
            return parseInt(item, 10);
        });
        all_scores = all_scores.sort(compareNumbers);
        all_scores = all_scores.reverse();
        all_scores = all_scores.slice(0,Math.min(1, all_scores.length));
        let weights = new Array(all_scores.length).fill(0);
        let to_add = 0;
        if(all_scores[all_scores.length - 1] < 0){
            to_add = Math.abs(all_scores[all_scores.length - 1]);
        }
        for (let i = 0; i < weights.length; i++){
            weights[i] = all_scores[i] + to_add + 1;
        }
        let chosen_score = weightedRandom(all_scores, weights);
        return { score: chosen_score, move: scores_moves[chosen_score][0] };
    }
    else
    {
        let min_score = checkmate + 1;

        for (const move of shuffled_valid_moves)
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

            if (next_move_result.score in scores_moves)
            {
                scores_moves[parseInt(next_move_result.score)].push(move)
            } else {
                scores_moves[parseInt(next_move_result.score)] = [move]
            }

            beta = Math.min(next_move_result.score, beta);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }
        let all_scores = Object.keys(scores_moves);
        if(all_scores.length == 0){
            return { score: checkmate, move: next_move};
        }
        all_scores = all_scores.map(function(item) {
            return parseInt(item, 10);
        });
        all_scores = all_scores.sort(compareNumbers);
        all_scores = all_scores.slice(0,Math.min(1, all_scores.length));
        let weights = new Array(all_scores.length).fill(0);
        let to_add = 0;
        if(all_scores[0] < 0){
            to_add = Math.abs(all_scores[0]);
        }
        for (let i = 0; i < weights.length; i++){
            weights[i] = all_scores[i] + to_add + 1;
        }
        let chosen_score = weightedRandom(all_scores, weights.reverse());
        return { score: chosen_score, move: scores_moves[chosen_score][0] };
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
            const weight = is_piece_white ? 1 : -1;

            score += weight * piece_weights[square[1]];
        }
    }

    return score;
}

export function score_board(game_state, is_ai_white)
{
    const weight = game_state.white_to_move ? 1 : -1;

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

export function find_stochastic_tree_search_best_move(game_state, valid_moves)
{
    const next_move_result =
        find_stochastic_tree_search_move(
            game_state,
            valid_moves,
            max_depth_sts,
            game_state.white_to_move,
            -checkmate,
            checkmate);

    return next_move_result.move;
}

function play_random_game(game_state, depth){
    if(depth == 0){
        return score_board(game_state, false);
    }

    let valid_moves =  game_state.get_valid_moves();
    if(valid_moves.length == 0){
        return score_board(game_state, false)
    }
    let random_move = valid_moves[Math.floor(Math.random()*valid_moves.length)];
    game_state.make_move(random_move)
    let score = play_random_game(game_state, depth-1);
    game_state.undo_move();
    return score

}

function find_stochastic_tree_search_move(
    game_state, valid_moves, depth, is_ai_white, alpha, beta)
{
    let next_move = null;

    if (depth == 0)
    {   
        let random_game_score = 0;
        for (let i = 0; i<GAMES; i+=1){
            random_game_score += play_random_game(game_state, GAME_DEPTH);
        }
        random_game_score /= GAMES;
        return { score: random_game_score};
    }

    if(valid_moves.length == 0){
        return { score: score_board(game_state, is_ai_white), move: next_move };
    }

    //Shufflig so it would look more rational
    let shuffled_valid_moves = valid_moves.sort(function () {
        return Math.random() - 0.5;
      });
    
    let scores_moves = {};

    if (game_state.white_to_move)
    {
        let max_score = -checkmate - 1;

        for (const move of shuffled_valid_moves)
        {
            game_state.make_move(move);

            const next_moves = game_state.get_valid_moves();
            const next_move_result =
            find_stochastic_tree_search_move(
                    game_state,
                    next_moves,
                    depth - 1,
                    is_ai_white,
                    alpha,
                    beta);

            if (next_move_result.score in scores_moves)
            {
               scores_moves[parseInt(next_move_result.score)].push(move)
            } else {
                scores_moves[parseInt(next_move_result.score)] = [move];
            }

            alpha = Math.max(next_move_result.score, alpha);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }
        let all_scores = Object.keys(scores_moves);
        if(all_scores.length == 0){
            return { score: -checkmate, move: next_move};
        }
        all_scores = all_scores.map(function(item) {
            return parseInt(item, 10);
        });
        all_scores = all_scores.sort(compareNumbers);
        all_scores = all_scores.reverse();
        all_scores = all_scores.slice(0,Math.min(1, all_scores.length));
        let weights = new Array(all_scores.length).fill(0);
        let to_add = 0;
        if(all_scores[all_scores.length - 1] < 0){
            to_add = Math.abs(all_scores[all_scores.length - 1]);
        }
        for (let i = 0; i < weights.length; i++){
            weights[i] = all_scores[i] + to_add + 1;
        }
        let chosen_score = weightedRandom(all_scores, weights);
        return { score: chosen_score, move: scores_moves[chosen_score][0] };
    }
    else
    {
        let min_score = checkmate + 1;

        for (const move of shuffled_valid_moves)
        {
            game_state.make_move(move);

            const next_moves = game_state.get_valid_moves();
            const next_move_result =
            find_stochastic_tree_search_move(
                    game_state,
                    next_moves,
                    depth - 1,
                    is_ai_white,
                    alpha,
                    beta);

            if (next_move_result.score in scores_moves)
            {
                scores_moves[parseInt(next_move_result.score)].push(move)
            } else {
                scores_moves[parseInt(next_move_result.score)] = [move]
            }

            beta = Math.min(next_move_result.score, beta);
            game_state.undo_move();

            if (beta <= alpha)
            {
                break;
            }
        }
        let all_scores = Object.keys(scores_moves);
        if(all_scores.length == 0){
            return { score: checkmate, move: next_move};
        }
        all_scores = all_scores.map(function(item) {
            return parseInt(item, 10);
        });
        all_scores = all_scores.sort(compareNumbers);
        all_scores = all_scores.slice(0,Math.min(1, all_scores.length));
        let weights = new Array(all_scores.length).fill(0);
        let to_add = 0;
        if(all_scores[0] < 0){
            to_add = Math.abs(all_scores[0]);
        }
        for (let i = 0; i < weights.length; i++){
            weights[i] = all_scores[i] + to_add + 1;
        }
        let chosen_score = weightedRandom(all_scores, weights.reverse());
        return { score: chosen_score, move: scores_moves[chosen_score][0] };
    }
}
