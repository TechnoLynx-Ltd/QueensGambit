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

export async function init()
{
    load_model();
    await init_hand_pose_interface();

    document.getElementById("loader").style.display = "none";
    document.getElementById("myDiv").style.display = "block";

    canvasDiv = document.getElementById("canvasdiv");
    canvas = document.getElementById("canvas");
    canvas.width = Math.floor(canvasDiv.offsetWidth*0.9)
    canvas.height = Math.floor(canvasDiv.offsetWidth*0.9)
    context = canvas.getContext("2d");
    square_width = Math.floor(canvas.width / dimension);
    square_height = Math.floor(canvas.height / dimension);
    canvas.addEventListener("click", board_click);

    

    for (let [name, image] of Object.entries(image_map))
    {
        images[name] = new Image(square_width, square_height);
        images[name].onload = draw_pieces;
        images[name].src = image;
    }

    
    draw_board();
    display_ai();
    draw_message("Please, choose a type for the AI model");
    valid_moves = game_state.get_valid_moves();

}

export async function turn_on_hand_tracking()
{
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
    display_ai();

    refresh_state();
}

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
            move = find_minmax_best_move(game_state, valid_moves);
            break;
        }
        case "ANN":
        {
            move = find_model_best_move(game_state, valid_moves);
            break;
        }
        case "Stochastic Tree Search":
        {
            move = find_stochastic_tree_search_best_move(game_state, valid_moves);
            break;
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