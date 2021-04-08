"""
Module to control the chess engine by handling user input
"""

import pygame as p
import os
from tensorflow import keras

import ai
import engine

# Constants
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def print_workspace():
    """
    Sanity check
    """
    print(os.listdir())


def init_images():
    """
    Initialize images
    """
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]
    path = "../../resources/images/"
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(path + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """
    Main driver
    """
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    init_images()
    running = True
    selected_square = ()
    player_clicks = []
    valid_moves = gs.get_valid_moves()
    made_move = False
    game_over = False
    white_ai = True
    black_ai = False

    # Load trained model
    model = keras.models.load_model('../../model')

    while running:
        human_turn = (gs.white_to_move and not white_ai) or (not gs.white_to_move and not black_ai)
        for e in p.event.get():
            # if not game_over:
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    selected_square, player_clicks, made_move = play_human_turn(selected_square, player_clicks,
                                                                                valid_moves, gs, made_move)

                elif not game_over and not human_turn:
                    # chosen_move = ChessAI.find_minmax_best_move(gs, valid_moves)
                    chosen_move = ai.find_model_best_move(gs, valid_moves, model)
                    gs.make_move(chosen_move)
                    made_move = True

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    made_move = True
                    game_over = False
                if e.key == p.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_square = ()
                    player_clicks = []
                    made_move = False
                    game_over = False

        if made_move:
            valid_moves = gs.get_valid_moves()
            made_move = False

        draw_game_state(screen, gs, valid_moves, selected_square)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs, valid_moves, selected_square):
    """
    Graphics handler methods
    """
    draw_board(screen)
    highlight_square(screen, gs, valid_moves, selected_square)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    """
    Draw squares
    """
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    """
    Draw pieces
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_square(screen, gs, valid_moves, selected_square):
    """
    Highlight possible moves
    """
    if selected_square != ():
        r, c = selected_square
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color("red"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_text(screen, text):
    """
    Print text on board
    """
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("blue"))
    text_loc = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_loc)


def play_human_turn(selected_square, player_clicks, valid_moves, gs, made_move):
    """
    Play human turn
    """
    location = p.mouse.get_pos()
    col = location[0] // SQ_SIZE
    row = location[1] // SQ_SIZE

    # If the user clicked the same square twice
    if selected_square == (row, col):
        selected_square == ()
        player_clicks = []
    else:
        selected_square = (row, col)
        player_clicks.append(selected_square)
    if len(player_clicks) == 2:
        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
        for i in range(len(valid_moves)):
            if move == valid_moves[i]:
                gs.make_move(valid_moves[i])
                made_move = True
                selected_square = ()
                player_clicks = []
        if not made_move:
            player_clicks = [selected_square]

    return selected_square, player_clicks, made_move


if __name__ == "__main__":
    main()

    # dparser = ChessUtil.DataParser()
    # dparser.file_test()
