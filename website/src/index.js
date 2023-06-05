import { Game_state, Move } from "./engine.js";
import { find_minmax_best_move, find_stochastic_tree_search_best_move } from "./minmax.js";
import { load_model, find_model_best_move } from "./ann.js";
import { init_hand_pose_interface, detect_hand } from "./handpose_chess_interface.js"


import bB from "../../resources/images/bB.png";
import bK from "../../resources/images/bK.png";
import bN from "../../resources/images/bN.png";
import bR from "../../resources/images/bR.png";
import bQ from "../../resources/images/bQ.png";
import bP from "../../resources/images/bP.png";
import wB from "../../resources/images/wB.png";
import wK from "../../resources/images/wK.png";
import wN from "../../resources/images/wN.png";
import wR from "../../resources/images/wR.png";
import wQ from "../../resources/images/wQ.png";
import wP from "../../resources/images/wP.png";

var blobURL = URL.createObjectURL( new Blob([ '(',

function(){
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

self.onmessage = (data) => {

    console.log(data);
    gs = new Game_state();
    gs.from_object(JSON.parse(data['data'][1]));
    valid_moves = gs.get_valid_moves();
    let move = null; 
    if(data['data'][0] == "MinMax"){
        move = find_minmax_best_move(gs, valid_moves);
    } else{
        move = find_stochastic_tree_search_best_move(gs, valid_moves);
    }
    postMessage(["READY", JSON.stringify(move), JSON.stringify(gs)]);
};

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
            max_depth_minmax,
            game_state.white_to_move,
            -checkmate,
            checkmate);

    return next_move_result.move;
}


function weightedRandom(items, weights) {
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

function score_board(game_state, is_ai_white)
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

function find_stochastic_tree_search_best_move(game_state, valid_moves)
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


class Game_state {
    constructor() {
        this.board =
            [
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
            ];


        this.position_dict =
        {
            "wP": 0,
            "wR": 1,
            "wN": 2,
            "wB": 3,
            "wQ": 4,
            "wK": 5,
            "bP": 6,
            "bR": 7,
            "bN": 8,
            "bB": 9,
            "bQ": 10,
            "bK": 11
        };

        this.knight_offsets =
            [
                [2, 1],
                [2, -1],
                [1, 2],
                [1, -2],
                [-1, 2],
                [-1, -2],
                [-2, -1],
                [-2, 1]
            ];

        this.rook_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]];
        this.bishop_moves = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
        this.all_directions = this.rook_moves.concat(this.bishop_moves);

        this.move_methods = {
            'P': this.get_pawn_moves,
            'R': this.get_rook_moves,
            'N': this.get_knight_moves,
            'B': this.get_bishop_moves,
            'Q': this.get_queen_moves,
            'K': this.get_king_moves
        };

        this.current_castle_rights = new Castle_rights(true, true, true, true);
        this.white_to_move = true;
        this.move_log = [];
        this.white_king_location = [7, 4];
        this.black_king_location = [0, 4];
        this.en_passant_location = [];
        this.castle_rights_log =
            [JSON.parse(JSON.stringify(this.current_castle_rights))];
        this.in_check = false;
        this.pins = [];
        this.checks = [];
        this.checkmate = false;
        this.stalemate = false;
        this.promotion_pieces = ['Q', 'R', 'B', 'N'];
    }

    from_object(object) {
        this.board = object.board;


        this.position_dict =
        {
            "wP": 0,
            "wR": 1,
            "wN": 2,
            "wB": 3,
            "wQ": 4,
            "wK": 5,
            "bP": 6,
            "bR": 7,
            "bN": 8,
            "bB": 9,
            "bQ": 10,
            "bK": 11
        };

        this.knight_offsets =
            [
                [2, 1],
                [2, -1],
                [1, 2],
                [1, -2],
                [-1, 2],
                [-1, -2],
                [-2, -1],
                [-2, 1]
            ];

        this.rook_moves = [[1, 0], [-1, 0], [0, 1], [0, -1]];
        this.bishop_moves = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
        this.all_directions = this.rook_moves.concat(this.bishop_moves);

        this.move_methods = {
            'P': this.get_pawn_moves,
            'R': this.get_rook_moves,
            'N': this.get_knight_moves,
            'B': this.get_bishop_moves,
            'Q': this.get_queen_moves,
            'K': this.get_king_moves
        };

        this.current_castle_rights = new Castle_rights(object.current_castle_rights);
        this.white_to_move = object.white_to_move;
        this.move_log = object.move_log;
        this.white_king_location = object.white_king_location;
        this.black_king_location = object.black_king_location;
        this.en_passant_location = object.en_passant_location;
        this.castle_rights_log =
            [JSON.parse(JSON.stringify(this.current_castle_rights))];
        this.in_check = object.in_check;
        this.pins = object.pins;
        this.checks = object.checks;
        this.checkmate = object.checkmate;
        this.stalemate = object.stalemate;
        this.promotion_pieces = ['Q', 'R', 'B', 'N'];
    }

    get_position() {
        let result = [];

        for (let row = 0; row < 8; ++row) {
            result[row] = [];

            for (let column = 0; column < 8; ++column) {
                result[row][column] = []

                for (let piece_index = 0; piece_index < 12; ++piece_index) {
                    result[row][column][piece_index] = 0;
                }

                const piece_index =
                    this.position_dict[this.board[row][column]];

                result[row][column][piece_index] = 1;
            }
        }

        return result;
    }

    update_castle_rights(move) {
        if (this.white_to_move) {
            if (move.piece_moved == "wK") {
                this.current_castle_rights.white_king_side = false;
                this.current_castle_rights.white_queen_side = false;
            }

            if (move.piece_moved == "wR" && move.start[0] == 7) {
                if (move.start[1] == 0) {
                    this.current_castle_rights.white_queen_side = false;
                }

                if (move.start[1] == 7) {
                    this.current_castle_rights.white_king_side = false;
                }
            }

            if (move.piece_captured == "bR" && move.end[0] == 0) {
                if (move.end[1] == 0) {
                    this.current_castle_rights.black_queen_side = false;
                }

                if (move.end[1] == 7) {
                    this.current_castle_rights.black_king_side = false;
                }
            }
        }
        else {
            if (move.piece_moved == "bK") {
                this.current_castle_rights.black_king_side = false;
                this.current_castle_rights.black_queen_side = false;
            }

            if (move.piece_moved == "bR" && move.start[0] == 0) {
                if (move.start[1] == 0) {
                    this.current_castle_rights.black_queen_side = false;
                }

                if (move.start[1] == 7) {
                    this.current_castle_rights.black_king_side = false;
                }
            }

            if (move.piece_captured == "wR" && move.end[0] == 7) {
                if (move.end[1] == 0) {
                    this.current_castle_rights.white_queen_side = false;
                }

                if (move.end[1] == 7) {
                    this.current_castle_rights.white_king_side = false;
                }
            }
        }
    }

    make_move(move) {
        this.board[move.start[0]][move.start[1]] = "--";

        if (move.promotion_move) {
            const color = this.white_to_move ? "w" : "b";
            this.board[move.end[0]][move.end[1]] = color + move.promote_to;
        }
        else {
            this.board[move.end[0]][move.end[1]] = move.piece_moved;
        }

        if (move.en_passant_move) {
            const direction = this.white_to_move ? 1 : -1;

            this.board[move.end[0] + direction][move.end[1]] = "--";
        }

        if (move.castle_move) {
            const offset1 = (move.end[1] == 2) ? 1 : -1;
            const offset2 = (move.end[1] == 2) ? -2 : 1;
            let row = this.board[move.end[0]];

            row[move.end[1] + offset1] = row[move.end[1] + offset2];
            row[move.end[1] + offset2] = "--";
        }

        // Castle rights update
        this.update_castle_rights(move);
        this.castle_rights_log.push(
            JSON.parse(JSON.stringify(this.current_castle_rights)));

        this.move_log.push(move);
        this.white_to_move = !this.white_to_move;

        // King position
        if (move.piece_moved == "wK") {
            this.white_king_location = move.end;
        }
        else if (move.piece_moved == "bK") {
            this.black_king_location = move.end;
        }

        // En passant location update
        if (move.piece_moved == "wP" && move.end[0] == 4) {
            this.en_passant_location = [move.end[0] + 1, move.end[1]];
        }
        else if (move.piece_moved == "bP" && move.end[0] == 3) {
            this.en_passant_location = [move.end[0] - 1, move.end[1]];
        }
        else {
            this.en_passant_location = [];
        }
    }

    undo_move() {
        if (this.move_log.length == 0) {
            return;
        }

        const last_move = this.move_log.pop();

        if (last_move.promotion_move) {
            const color = this.white_to_move ? "b" : "w";

            this.board[last_move.end[0]][last_move.end[1]] =
                last_move.piece_captured;
            this.board[last_move.start[0]][last_move.start[1]] = color + 'P';
        }
        else if (last_move.en_passant_move) {
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;
            this.board[last_move.end[0]][last_move.end[1]] = "--";

            if (this.white_to_move) {
                this.board[last_move.end[0] - 1][last_move.end[1]] = "wP";
            }
            else {
                this.board[last_move.end[0] + 1][last_move.end[1]] = "bP";
            }
        }
        else if (last_move.castle_move) {
            let end_row = this.board[last_move.end[0]];

            end_row[last_move.end[1]] = "--";
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;

            if (last_move.end[1] == 2) {
                end_row[last_move.end[1] - 2] = end_row[last_move.end[1] + 1];
                end_row[last_move.end[1] + 1] = "--";
            }
            else {
                end_row[last_move.end[1] + 1] = end_row[last_move.end[1] - 1];
                end_row[last_move.end[1] - 1] = "--";
            }
        }
        else {
            this.board[last_move.end[0]][last_move.end[1]] =
                last_move.piece_captured;
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;
        }

        // King position
        this.white_to_move = !this.white_to_move;

        if (last_move.piece_moved == "wK") {
            this.white_king_location = last_move.start;
        }
        else if (last_move.piece_moved == "bK") {
            this.black_king_location = last_move.start;
        }

        // To be able to restore the en passant location
        //    we need to look back at 1 more element
        this.en_passant_location = [];

        if (this.move_log.length > 0) {
            const previous_move = this.move_log.at(-1);

            if (previous_move.piece_moved == "wP" && previous_move.end[0] == 4) {
                this.en_passant_location =
                    [previous_move.end[0] + 1, previous_move.end[1]];
            }
            else if (
                previous_move.piece_moved == "bP" && previous_move.end_row == 3) {
                this.en_passant_location =
                    [previous_move.end[0] - 1, previous_move.end[1]];
            }
        }

        // Undo castle rights
        this.castle_rights_log.pop();
        this.current_castle_rights =
            JSON.parse(JSON.stringify(this.castle_rights_log.at(-1)));

        // Set checkmate and stalemate to false
        this.checkmate = false;
        this.stalemate = false;
    }

    // All moves considering checks
    get_valid_moves() {
        const king_location =
            this.white_to_move ?
                this.white_king_location :
                this.black_king_location;
        const king_row = king_location[0];
        const king_column = king_location[1];
        const pin_checks_result = this.get_pins_checks();
        let moves = [];

        this.in_check = pin_checks_result.in_check;
        this.pins = pin_checks_result.pins;
        this.checks = pin_checks_result.checks;

        if (this.in_check) {
            if (this.checks.length == 1) {
                const check = this.checks[0];
                const check_piece =
                    this.board[check.location[0]][check.location[1]];
                let valid_squares = [];

                moves = this.get_all_possible_moves();

                if (check_piece[1] == "N") {
                    valid_squares = [check.location];
                }
                else {
                    for (let i = 1; i < 8; ++i) {
                        const valid_square =
                            [
                                king_row + check.direction[0] * i,
                                king_column + check.direction[1] * i
                            ];

                        valid_squares.push(valid_square);

                        if (
                            valid_square[0] == check.location[0] &&
                            valid_square[1] == check.location[1]) {
                            break;
                        }
                    }
                }

                for (let i = moves.length - 1; i > -1; --i) {
                    if (moves[i].piece_moved[1] != "K") {
                        let found = false;

                        for (const valid_square of valid_squares) {
                            if (
                                valid_square[0] == moves[i].end[0] &&
                                valid_square[1] == moves[i].end[1]) {
                                found = true;
                                break;
                            }
                        }

                        if (!found) {
                            moves.splice(i, 1);
                        }
                    }
                }
            }
            // Double check
            else {
                this.get_king_moves(king_row, king_column, moves);
            }
        }
        else {
            moves = this.get_all_possible_moves();
        }

        if (moves.length == 0) {
            if (this.in_check) {
                this.checkmate = true;
            }
            else {
                this.stalemate = true;
            }
        }

        return moves;
    }

    // All moves without considering checks
    get_all_possible_moves() {
        let moves = [];

        for (let row = 0; row < this.board.length; ++row) {
            for (let column = 0; column < this.board[row].length; ++column) {
                let player = this.board[row][column][0];
                let current_color = this.white_to_move ? "w" : "b";

                if (player == current_color) {
                    let piece = this.board[row][column][1];

                    this.move_methods[piece].call(this, row, column, moves);
                }
            }
        }

        return moves;
    }

    get_pins_checks() {
        let pins = [];
        let checks = [];
        let in_check = false;

        let king_row;
        let king_column;
        let actor_color;
        let enemy_color;

        if (this.white_to_move) {
            king_row = this.white_king_location[0];
            king_column = this.white_king_location[1];
            actor_color = "w";
            enemy_color = "b";
        }
        else {
            king_row = this.black_king_location[0];
            king_column = this.black_king_location[1];
            actor_color = "b";
            enemy_color = "w";
        }

        const directions =
            [
                [-1, 0],
                [0, -1],
                [1, 0],
                [0, 1],
                [-1, -1],
                [-1, 1],
                [1, -1],
                [1, 1]
            ];
        for (let i = 0; i < directions.length; ++i) {

            const direction = directions[i];
            let possible_pin = null;

            for (let j = 1; j < 8; ++j) {
                const test_row = king_row + direction[0] * j;
                const test_column = king_column + direction[1] * j;

                // Off the board
                if (!check_indices(test_row, test_column)) {
                    break;
                }
                const end_piece = this.board[test_row][test_column];

                if (end_piece[0] == actor_color && end_piece[1] != 'K') {
                    if (possible_pin == null) {
                        possible_pin =
                        {
                            location: [test_row, test_column],
                            direction: direction
                        };
                    }
                    else {
                        // More than one piece blocking so it's not a pin
                        break;
                    }
                }
                else if (end_piece[0] == enemy_color) {
                    const type = end_piece[1];
                    const rook = (0 <= i && i <= 3 && type == "R");
                    const bishop = (4 <= i && i <= 7 && type == "B");
                    const pawn_direction_white =
                        (enemy_color == "w" && 6 <= i && i <= 7);
                    const pawn_direction_black =
                        (enemy_color == "b" && 4 <= i && i <= 5);
                    const pawn_direction =
                        (pawn_direction_white || pawn_direction_black);
                    const pawn = (j == 1 && type == "P" && pawn_direction);
                    const king = (j == 1 && type == "K");
                    const queen = (type == "Q");
                    if (rook || bishop || pawn || queen || king) {
                        // No piece blocking so check
                        if (possible_pin == null) {
                            in_check = true;

                            checks.push(
                                {
                                    location: [test_row, test_column],
                                    direction: direction
                                });

                            break
                        }
                        // Allied piece blocking so pin
                        else {
                            pins.push(possible_pin);
                            break;
                        }
                    }
                    // No check
                    else {
                        break;
                    }
                }
            }
        }
        for (const direction of this.knight_offsets) {
            const test_row = king_row + direction[0];
            const test_column = king_column + direction[1];

            if (!check_indices(test_row, test_column)) {
                continue;
            }

            const piece = this.board[test_row][test_column];

            if (piece == enemy_color + "N") {
                in_check = true;

                checks.push(
                    {
                        location: [test_row, test_column],
                        direction: direction
                    });
            }
        }

        return { in_check: in_check, pins: pins, checks: checks };
    }

    get_pin_state(row, column) {
        for (let i = this.pins.length - 1; i > -1; --i) {
            const location = this.pins[i].location;

            if (location[0] == row && location[1] == column) {
                const pin = this.pins[i];
                const direction = [pin.direction[0], pin.direction[1]];

                this.pins.splice(i, 1);

                return { direction: direction, pinned: true };
            }
        }

        return { direction: [], pinned: false };
    }

    get_pawn_moves(row, column, moves) {
        const pin_state = this.get_pin_state(row, column);
        const y = (this.white_to_move ? -1 : 1);
        const front_empty = this.board[row + y][column] == "--";

        if (front_empty && check_direction(pin_state, [y, 0])) {
            let current_move = new Move([row, column], [row + y, column], this.board);
            if (current_move.promotion_move) {
                for (let promoting of this.promotion_pieces) {
                    moves.push(
                        new Move([row, column], [row + y, column], this.board, false, false, promoting));
                }
            } else {
                moves.push(
                    new Move([row, column], [row + y, column], this.board));
            }
            // moves.push(
            //     new Move([ row, column ], [ row + y, column ], this.board));

            const initial_row = (this.white_to_move ? 6 : 1);

            if (row == initial_row && this.board[row + 2 * y][column] == "--") {
                moves.push(
                    new Move(
                        [row, column], [row + 2 * y, column], this.board));
            }
        }

        let x_directions = [-1, 1];

        for (const x of x_directions) {
            const enemy_color = (this.white_to_move ? "b" : "w");

            if (column + x < 0 || column + x > 7) {
                continue;
            }

            if (!check_direction(pin_state, [y, x])) {
                continue;
            }

            if (this.board[row + y][column + x][0] == enemy_color) {
                moves.push(
                    new Move(
                        [row, column], [row + y, column + x], this.board));
            }
            else if (
                this.en_passant_location[0] == row + y &&
                this.en_passant_location[1] == column + x) {
                moves.push(
                    new Move(
                        [row, column],
                        [row + y, column + x],
                        this.board,
                        true));
            }
        }
    }

    find_all_moves(row, column, moves, directions, one_step = false) {
        const pin_state = this.get_pin_state(row, column);
        const color = this.white_to_move ? "b" : "w";

        for (const direction of directions) {
            if (!check_double_direction(pin_state, direction)) {
                continue;
            }

            let current_row = row + direction[0];
            let current_column = column + direction[1];
            let blocked = !check_indices(current_row, current_column);

            while (!blocked) {
                let push_new = false;

                if (this.board[current_row][current_column] == "--") {
                    push_new = true;
                }
                else {
                    blocked = true;

                    if (this.board[current_row][current_column][0] == color) {
                        push_new = true;
                    }
                }

                if (push_new) {
                    moves.push(
                        new Move(
                            [row, column],
                            [current_row, current_column],
                            this.board));
                }

                current_row += direction[0];
                current_column += direction[1];
                blocked =
                    blocked || !check_indices(current_row, current_column);
                blocked = blocked || one_step;
            }
        }
    }

    get_rook_moves(row, column, moves) {
        this.find_all_moves(row, column, moves, this.rook_moves);
    }

    get_bishop_moves(row, column, moves) {
        this.find_all_moves(row, column, moves, this.bishop_moves);
    }

    get_queen_moves(row, column, moves) {
        this.find_all_moves(row, column, moves, this.all_directions);
    }

    get_knight_moves(row, column, moves) {
        this.find_all_moves(row, column, moves, this.knight_offsets, true);
    }

    get_king_moves(row, column, moves) {
        const enemy_color = this.white_to_move ? "b" : "w";

        this.get_castle_moves(row, column, moves);

        for (const direction of this.all_directions) {
            const current_row = row + direction[0];
            const current_column = column + direction[1];
            let pin_checks_result = {};
            let king_location =
                this.white_to_move ?
                    this.white_king_location :
                    this.black_king_location;

            if (!check_indices(current_row, current_column)) {
                continue;
            }

            if (this.white_to_move) {
                this.white_king_location[0] = current_row;
                this.white_king_location[1] = current_column;
                pin_checks_result = this.get_pins_checks();
                this.white_king_location[0] = row;
                this.white_king_location[1] = column;
            } else {
                this.black_king_location[0] = current_row;
                this.black_king_location[1] = current_column;
                pin_checks_result = this.get_pins_checks();
                this.black_king_location[0] = row;
                this.black_king_location[1] = column;
            }

            if (!pin_checks_result.in_check) {
                const current_square = this.board[current_row][current_column];

                if (current_square == "--" || current_square[0] == enemy_color) {
                    moves.push(
                        new Move(
                            [row, column],
                            [current_row, current_column],
                            this.board));
                }
            }
        }
    }

    get_castle_side_moves(
        row, column, moves, king_location, direction, square_count) {
        for (let i = 1; i <= square_count; ++i) {
            if (this.board[row][column + i * direction] != "--") {
                return;
            }
        }

        king_location[1] = column + direction;
        let pin_checks_result1 = this.get_pins_checks();
        king_location[1] = column + 2 * direction;
        let pin_checks_result2 = this.get_pins_checks();
        king_location[1] = column;

        if (!pin_checks_result1.in_check && !pin_checks_result2.in_check) {
            moves.push(
                new Move(
                    [row, column],
                    [row, column + 2 * direction],
                    this.board,
                    false,
                    true));
        }
    }

    get_castle_moves(row, column, moves) {
        if (this.in_check) {
            return;
        }

        const white_king_side =
            this.white_to_move && this.current_castle_rights.white_king_side;
        const white_queen_side =
            this.white_to_move && this.current_castle_rights.white_queen_side;
        const black_king_side =
            !this.white_to_move && this.current_castle_rights.black_king_side;
        const black_queen_side =
            !this.white_to_move && this.current_castle_rights.black_queen_side;
        let king_location =
            this.white_to_move ?
                this.white_king_location :
                this.black_king_location;
        let direction;
        let square_count;

        if (white_king_side || black_king_side) {
            this.get_castle_side_moves(row, column, moves, king_location, 1, 2);
        }

        if (white_queen_side || black_queen_side) {
            this.get_castle_side_moves(
                row, column, moves, king_location, -1, 3);
        }
    }
}

class Move {
    constructor(start, end, board, en_passant_move = false, castle_move = false, promote_to = 'Q') {
        this.start = start;
        this.end = end;
        this.piece_moved = board[this.start[0]][this.start[1]];
        this.piece_captured = board[this.end[0]][this.end[1]];
        this.move_id =
            this.start[0] * 1000 +
            this.start[1] * 100 +
            this.end[0] * 10 +
            this.end[1];
        this.promotion_move = false;
        this.en_passant_move = en_passant_move;
        this.castle_move = castle_move;
        this.promote_to = promote_to

        const white_promotion = (this.end[0] == 0 && this.piece_moved == "wP");
        const black_promotion = (this.end[0] == 7 && this.piece_moved == "bP");

        if (white_promotion || black_promotion) {
            this.promotion_move = true;
        }
    }

    equals(other) {
        return this.move_id == other.move_id && this.promote_to == other.promote_to;
    }
}

class Castle_rights {
    constructor(
        white_queen_side, white_king_side, black_queen_side, black_king_side) {
        this.white_queen_side = white_queen_side;
        this.white_king_side = white_king_side;
        this.black_queen_side = black_queen_side;
        this.black_king_side = black_king_side;
    }
}

function check_direction(pin_state, direction) {
    const same_direction =
        pin_state.direction[0] == direction[0] &&
        pin_state.direction[1] == direction[1];

    if (!pin_state.pinned || same_direction) {
        return true;
    }
    else {
        return false;
    }
}

function check_double_direction(pin_state, direction) {
    const opposite_direction =
        pin_state.direction[0] == -direction[0] &&
        pin_state.direction[1] == -direction[1];

    return check_direction(pin_state, direction) || opposite_direction;
}

function check_indices(row, column) {
    return (0 <= row && row <= 7 && 0 <= column && column <= 7);
}

}.toString(),

')()' ], { type: 'application/javascript' } ) );

let my_worker = new Worker( blobURL );

// Won't be needing this anymore
URL.revokeObjectURL( blobURL );

let image_map =
{
    "bB": bB,
    "bK": bK,
    "bN": bN,
    "bR": bR,
    "bQ": bQ,
    "bP": bP,
    "wB": wB,
    "wK": wK,
    "wN": wN,
    "wR": wR,
    "wQ": wQ,
    "wP": wP,
};

let images = {};

let canvas, context;
let square_width, square_height;
let selected_square = null;
let player_clicks = [];
let white_ai = false;
let black_ai = true;
let valid_moves = [];
let dimension = 8;
let game_state = new Game_state();
let game_over = false;
let made_move = false;
let ai_type = "";
let canvasDiv;
let isHandTracking = false;
let handTrackingInitialized = false;
let reset_possible = true;
let reset_clicked = false;


export async function init()
{
    load_model();

    document.getElementById("loader").style.display = "none";
    document.getElementById("boardDiv").style.display = "block";

    canvasDiv = document.getElementById("canvasdiv");
    canvas = document.getElementById("canvas");
    canvas.width = Math.floor(canvasDiv.offsetWidth*0.9)
    canvas.height = Math.floor(canvasDiv.offsetWidth*0.9)
    context = canvas.getContext("2d");
    square_width = Math.floor(canvas.width / dimension);
    square_height = Math.floor(canvas.height / dimension);
    
    
    for (let [name, image] of Object.entries(image_map))
    {
        images[name] = new Image(square_width, square_height);
        images[name].onload = draw_pieces;
        images[name].src = image;
    }

    
    draw_board();
    draw_message("Select an AI model and press Start Game button to play a game.")

}

export async function start_game()
{
    canvas.addEventListener("click", board_click);
    display_ai();
    valid_moves = game_state.get_valid_moves();

    var e = document.getElementById("modelsDropDown");
    var aitype = e.value;
    start_with_model(aitype)
}

export async function new_reset_click()
{
    if(!reset_possible){
        reset_clicked = true;
        draw_message("Please wait until AI will make the move, after that the board will be reset automatically");
    } else {
        reset_clicked = false;
        canvas.removeEventListener("click", board_click);
        game_state = new Game_state();
        valid_moves = game_state.get_valid_moves();
        selected_square = null;
        player_clicks = [];
        made_move = false;
        game_over = false;
        ai_type = "";
        display_ai();
        draw_message("Select an AI model and press Start Game button to play a game.")
        display_ai();
        //refresh_state();
        draw_game_state()
    }
}



function start_with_model(aitype)
{
    if (ai_type.length == 0) {
        ai_type = aitype;
        display_ai();
        draw_message("Please, choose a piece to move by clicking on it, then wait for your AI opponent.");
    }
    else
        draw_message("You can't change the type of AI model during the game. Please, press reset and start-over");
}

export async function turn_on_hand_tracking()
{
    document.getElementById("hand_tracking_status").innerHTML =
    "Hand tracking model is loading in the backgroud...";
    await init_hand_pose_interface();
    document.getElementById("hand_tracking_status").innerHTML =
    "Hand tracking model is loaded!";
    isHandTracking = true;
    hand_tracking_loop();
}


async function hand_tracking_loop() {
    if(isHandTracking) {
        var hand_detection = await detect_hand();
        if(hand_detection['is_hand_present'] == true) {
            if(hand_detection['is_click'] == true) {
                await board_click2([hand_detection['position'][1], hand_detection['position'][0]])
            }
            draw_game_state();
            highlight_hand_position(hand_detection['position']);
            
        }
        requestAnimationFrame(hand_tracking_loop)
    }
}

function highlight_hand_position(hand_position) {
    let row = hand_position[1];
    let column = hand_position[0];

    context.globalAlpha = 0.5;
    context.fillStyle = "Yellow";
    context.fillRect(
        column * square_width,
        row * square_height,
        square_width,
        square_height);
}

export function undo_click()
{
    if (!this.white_to_move) {
        game_state.undo_move();
    }
    game_state.undo_move();
    made_move = true;
    game_over = false;

    refresh_state();
}

export function reset_click()
{
    game_state = new Game_state();
    valid_moves = game_state.get_valid_moves();
    selected_square = null;
    player_clicks = [];
    made_move = false;
    game_over = false;
    ai_type = "";
    draw_message("Select an AI model and press Start Game button to play a game.")
    display_ai();

    refresh_state();
}
// let my_worker = new Worker(new URL('./minmax.js', import.meta.url));


export function minmax_click()
{
    if (ai_type.length == 0) {
        ai_type = "MinMax";
        display_ai();
        draw_message("Please, choose a piece to move by clicking on it, then wait for your AI opponent.");
    }
    else
        draw_message("You can't change the type of AI model during the game. Please, press reset and start-over");
}

export function ann_click()
{
    if (ai_type.length == 0) {
        ai_type = "ANN";
        display_ai();
        draw_message("Please, choose a piece to move by clicking on it, then wait for your AI opponent.");
    }
    else
        draw_message("You can't change the type of AI model during the game. Please, press reset and start-over");

}

export function sts_click(){
    if (ai_type.length == 0) {
        ai_type = "Stochastic Tree Search";
        display_ai();
        draw_message("Please, choose a piece to move by clicking on it, then wait for your AI opponent.");
    }
    else
        draw_message("You can't change the type of AI model during the game. Please, press reset and start-over");

}

function draw_board()
{
    let square_colors = ["LightGray", "DarkGray"];

    context.globalAlpha = 1;

    for (let r = 0; r < dimension; ++r)
    {
        for (let c = 0; c < dimension; ++c)
        {
            context.fillStyle = square_colors[(r + c) % 2];
            context.fillRect(
                c * square_width,
                r * square_height,
                square_width,
                square_height);
        }
    }
}

function draw_pieces()
{
    context.globalAlpha = 1;

    for (let r = 0; r < dimension; ++r)
    {
        for (let c = 0; c < dimension; ++c)
        {
            let piece = game_state.board[r][c];
            let piece_image = images[piece];

            if (piece != "--")
            {
                context.drawImage(
                    piece_image, c * square_width, r * square_height, square_width, square_height);
            }
        }
    }
}

function highlight_square()
{
    if (!selected_square)
    {
        return;
    }

    let row = selected_square[0];
    let column = selected_square[1];
    let current_letter = (game_state.white_to_move ? "w" : "b");

    if (game_state.board[row][column][0] != current_letter)
    {
        return;
    }

    context.globalAlpha = 0.5;
    context.fillStyle = "Green";
    context.fillRect(
        column * square_width,
        row * square_height,
        square_width,
        square_height);
    context.fillStyle = "Blue";

    for (const move of valid_moves)
    {
        if (move.start[0] == row && move.start[1] == column)
        {
            context.fillRect(
                move.end[1] * square_width,
                move.end[0] * square_height,
                square_width,
                square_height);
        }
    }
}

function draw_game_state()
{
    draw_board();
    draw_pieces();
    highlight_square();
}

function play_ai_turn()
{
    let move = null;

    display_ai("calculating");

    switch (ai_type)
    {
        case "MinMax":
        {
            reset_possible = false;
            my_worker.postMessage(["MinMax", JSON.stringify(game_state)]);
            break;
        }
        case "ANN":
        {
            move = find_model_best_move(game_state, valid_moves);
            break;
        }
        case "Stochastic Tree Search":
        {
            reset_possible = false;
            my_worker.postMessage(["STS", JSON.stringify(game_state)]);
            break;
        }
    }


    if (move)
    {
        display_ai("done");
        game_state.make_move(move);
        made_move = true;
    }
    else
    {
        draw_message("Could not determine move");
    }
}

my_worker.onmessage = function(event) {
    console.log(event.data)
    let move = null
    if (event.data[0] == "READY") {
        let retrieved = JSON.parse(event.data[1]);
        retrieved.board = JSON.parse(event.data[2]).board
        move = new Move(retrieved.start, retrieved.end, retrieved.board, retrieved.en_passant_move, retrieved.castle_move, retrieved.promote_to);

    }
    if (move)
    {
        display_ai("done");
        game_state.make_move(move);
        made_move = true;
    }
    else
    {
        draw_message("Could not determine move");
    }
    reset_possible = true;
    if (reset_clicked) {
        new_reset_click();
    }
    refresh_state()

};

function refresh_state()
{
    if (game_state.white_to_move) {
        draw_message("It is White's turn");
    }

    else {
        draw_message("It is Black's turn");
    }

    if (game_state.checkmate) {
        game_over = true;

        if (game_state.white_to_move) {
            draw_message("Black wins by checkmate");
        }
        else {
            draw_message("White wins by checkmate");
        }
    }

    else if (game_state.stalemate) {
        game_over = true;
        draw_message("Stalemate");
        if (game_state.white_to_move) {
            draw_message("Black wins by stalemate");
        }
        else {
            draw_message("White wins by stalemate");
        }
    }

    if (made_move) {
        valid_moves = game_state.get_valid_moves();
        made_move = false;
    }
    draw_game_state();
}

function play_human_turn(clicked_square)
{

    if (
        Array.isArray(selected_square) &&
        selected_square[0] == clicked_square[0] &&
        selected_square[1] == clicked_square[1])
    {
        selected_square = null;
        player_clicks = [];
    }
    else
    {
        selected_square = clicked_square;
        player_clicks.push(clicked_square);
        highlight_square();
    }

    if (player_clicks.length == 2)
    {
        const move = new Move(player_clicks[0], player_clicks[1], game_state.board);

        for (const valid_move of valid_moves)
        {
            if (move.equals(valid_move))
            {
                game_state.make_move(valid_move);
                made_move = true;
                selected_square = null;
                player_clicks = [];
            }
        }

        if (!made_move)
        {
            player_clicks = [ selected_square ];
        } else {
        }
    }
}

function delay(milliseconds){
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

async function board_click2(clicked_square)
{
    if (game_over)
    {
        return;
    }

    let is_white_human_turn = (game_state.white_to_move && !white_ai);
    let is_black_human_turn = (!game_state.white_to_move && !black_ai);

    if (is_white_human_turn || is_black_human_turn)
    {       
        play_human_turn(clicked_square);
        let human_finished = made_move;
        refresh_state();
        if(human_finished){
            await delay(500);
            play_ai_turn();
        }
        refresh_state();
    }
}

async function board_click(event)
{
    if (game_over)
    {
        return;
    }

    let is_white_human_turn = (game_state.white_to_move && !white_ai);
    let is_black_human_turn = (!game_state.white_to_move && !black_ai);

    if (is_white_human_turn || is_black_human_turn)
    {
        let coordinate_x = event.clientX - canvas.offsetLeft;
        let coordinate_y = event.clientY - canvas.offsetTop;
        let square_x = Math.floor(coordinate_x / square_width);
        let square_y = Math.floor(coordinate_y / square_height);
        let clicked_square = [square_y, square_x];

        play_human_turn(clicked_square);
        let human_finished = made_move;
        refresh_state();
        if(human_finished){
            await delay(500);
            play_ai_turn();
        }
        refresh_state();
    }
}

function display_ai(text = "")
{
    document.getElementById("ai_status").innerHTML =
        "Current AI model: " + ai_type + " " + text;
}

function draw_message(text)
{
    document.getElementById("game_status").innerHTML =
    "Game Status: " + text;
}