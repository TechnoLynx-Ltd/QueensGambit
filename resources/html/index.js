import { Game_state, Move } from "./engine.js";
import { find_minmax_best_move } from "./minmax.js";
import { load_model, find_model_best_move } from "./ann.js";

import bB from "../images/bB.png";
import bK from "../images/bK.png";
import bN from "../images/bN.png";
import bR from "../images/bR.png";
import bQ from "../images/bQ.png";
import bP from "../images/bP.png";
import wB from "../images/wB.png";
import wK from "../images/wK.png";
import wN from "../images/wN.png";
import wR from "../images/wR.png";
import wQ from "../images/wQ.png";
import wP from "../images/wP.png";

let canvas, context;
let square_width, square_height;
let selected_square = null;
let player_clicks = [];
let white_ai = true;
let black_ai = false;
let valid_moves = [];
let dimension = 8;
let game_state = new Game_state();
let game_over = false;
let made_move = false;
let ai_type = "MinMax";

export function init()
{
    load_model();
    canvas = document.getElementById("canvas");
    context = canvas.getContext("2d");
    square_width = canvas.width / 8;
    square_height = canvas.height / 8;
    canvas.addEventListener("click", board_click);

    document.getElementById("bB").src = bB;
    document.getElementById("bK").src = bK;
    document.getElementById("bN").src = bN;
    document.getElementById("bR").src = bR;
    document.getElementById("bQ").src = bQ;
    document.getElementById("bP").src = bP;
    document.getElementById("wB").src = wB;
    document.getElementById("wK").src = wK;
    document.getElementById("wN").src = wN;
    document.getElementById("wR").src = wR;
    document.getElementById("wQ").src = wQ;
    document.getElementById("wP").src = wP;

    draw_board();
    draw_pieces();
    display_ai();
    valid_moves = game_state.get_valid_moves();
}

export function undo_click()
{
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

    refresh_state();
}

export function minmax_click()
{
    ai_type = "MinMax";
    display_ai();
}

export function ann_click()
{
    ai_type = "ANN";
    display_ai();
}

export function player_click()
{
    ai_type = "Player";
    display_ai();
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
            let piece_image = document.getElementById(piece);

            if (piece != "--")
            {
                context.drawImage(
                    piece_image, c * square_width, r * square_height);
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
            move = find_minmax_best_move(game_state, valid_moves);
            break;
        }
        case "ANN":
        {
            move = find_model_best_move(game_state, valid_moves);
            break;
        }
        case "Player":
        {
            play_human_turn();
            return;
        }
    }

    display_ai("done");

    if (move)
    {
        game_state.make_move(move);
        made_move = true;
    }
    else
    {
        draw_message("Could not determine move");
    }
}

function refresh_state()
{
    if (made_move)
    {
        valid_moves = game_state.get_valid_moves();
        made_move = false;
    }

    draw_game_state();

    if (game_state.checkmate)
    {
        game_over = true;

        if (game_state.white_to_move)
        {
            draw_message("Black wins by checkmate");
        }
        else
        {
            draw_message("White wins by checkmate");
        }
    }

    if (game_state.stalemate)
    {
        game_over = true;
        draw_message("Stalemate");
    }
}

function play_human_turn()
{
    let coordinate_x = event.clientX - canvas.offsetLeft;
    let coordinate_y = event.clientY - canvas.offsetTop;
    let square_x = Math.floor(coordinate_x / square_width);
    let square_y = Math.floor(coordinate_y / square_height);
    let clicked_square = [square_y, square_x];

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
        }
    }
}

function board_click(event)
{
    if (game_over)
    {
        return;
    }

    let is_white_human_turn = (game_state.white_to_move && !white_ai);
    let is_black_human_turn = (!game_state.white_to_move && !black_ai);

    if (is_white_human_turn || is_black_human_turn)
    {
        play_human_turn();
    }
    else
    {
        play_ai_turn();
    }

    refresh_state();
}

function display_ai(text = "")
{
    document.getElementById("ai_status").innerHTML =
        "Current AI: " + ai_type + " " + text;
}

function draw_message(text)
{
    document.getElementById("messages").innerHTML = text;
}