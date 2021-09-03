var engine = new Object();

engine.game_state = new Object();

engine.game_state.board =
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

engine.game_state.position_dict =
{
    'wP': 0,
    'wR': 1,
    'wN': 2,
    'wB': 3,
    'wQ': 4,
    'wK': 5,
    'bP': 6,
    'bR': 7,
    'bN': 8,
    'bB': 9,
    'bQ': 10,
    'bK': 11
};

engine.game_state.current_castle_rights =
{
    white_queen_side : true,
    white_king_side: true,
    black_king_side: true,
    black_queen_side: true
};

engine.game_state.white_to_move = true;
engine.game_state.move_log = [];
engine.game_state.white_king_loc = { row: 7, column: 4};
engine.game_state.black_king_loc = { row: 0, column: 4};
engine.game_state.en_passant_loc = {};
engine.game_state.castle_rights_log =
    JSON.parse(JSON.stringify(engine.game_state.current_castle_rights));
engine.game_state.in_check = false;
engine.game_state.pins = [];
engine.game_state.checks = [];
engine.game_state.checkmate = false;
engine.game_state.stalemate = false;
engine.game_state.move_methods = {
    'P': engine.game_state.get_pawn_moves,
    'R': engine.game_state.get_rook_moves,
    'N': engine.game_state.get_knight_moves,
    'B': engine.game_state.get_bishop_moves,
    'Q': engine.game_state.get_queen_moves,
    'K': engine.game_state.get_king_moves
};