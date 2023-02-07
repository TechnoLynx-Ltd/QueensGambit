export class Game_state
{
    constructor()
    {
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

        this.board =
        [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "bK", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "bP"],
            ["--", "--", "--", "--", "--", "--", "wK", "--"]
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
            [ 2,  1],
            [ 2, -1],
            [ 1,  2],
            [ 1, -2],
            [-1,  2],
            [-1, -2],
            [-2, -1],
            [-2,  1]
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
        this.white_king_location = [ 7, 4 ];
        this.black_king_location = [ 0, 4 ];
        this.en_passant_location = [];
        this.castle_rights_log =
            [ JSON.parse(JSON.stringify(this.current_castle_rights)) ];
        this.in_check = false;
        this.pins = [];
        this.checks = [];
        this.checkmate = false;
        this.stalemate = false;
    }

    get_position()
    {
        let result = [];

        for (let row = 0; row < 8; ++row)
        {
            result[row] = [];

            for (let column = 0; column < 8; ++column)
            {
                result[row][column] = []

                for (let piece_index = 0; piece_index < 12; ++piece_index)
                {
                    result[row][column][piece_index] = 0;
                }

                const piece_index =
                    this.position_dict[this.board[row][column]];

                result[row][column][piece_index] = 1;
            }
        }

        return result;
    }

    update_castle_rights(move)
    {
        if (this.white_to_move)
        {
            if (move.piece_moved == "wK")
            {
                this.current_castle_rights.white_king_side = false;
                this.current_castle_rights.white_queen_side = false;
            }

            if (move.piece_moved == "wR" && move.start[0] == 7)
            {
                if (move.start[1] == 0)
                {
                    this.current_castle_rights.white_queen_side = false;
                }

                if (move.start[1] == 7)
                {
                    this.current_castle_rights.white_king_side = false;
                }
            }

            if (move.piece_captured == "bR" && move.end[0] == 0)
            {
                if (move.end[1] == 0)
                {
                    this.current_castle_rights.black_queen_side = false;
                }

                if (move.end[1] == 7)
                {
                    this.current_castle_rights.black_king_side = false;
                }
            }
        }
        else
        {
            if (move.piece_moved == "bK")
            {
                this.current_castle_rights.black_king_side = false;
                this.current_castle_rights.black_queen_side = false;
            }

            if (move.piece_moved == "bR" && move.start[0] == 0)
            {
                if (move.start[1] == 0)
                {
                    this.current_castle_rights.black_queen_side = false;
                }

                if (move.start[1] == 7)
                {
                    this.current_castle_rights.black_king_side = false;
                }
            }

            if (move.piece_captured == "wR" && move.end[0] == 7)
            {
                if (move.end[1] == 0)
                {
                    this.current_castle_rights.white_queen_side = false;
                }

                if (move.end[1] == 7)
                {
                    this.current_castle_rights.white_king_side = false;
                }
            }
        }
    }

    make_move(move)
    {
        this.board[move.start[0]][move.start[1]] = "--";

        if (move.promotion_move)
        {
            const color = this.white_to_move ? "w" : "b";

            this.board[move.end[0]][move.end[1]] = color + "Q";
        }
        else
        {
            this.board[move.end[0]][move.end[1]] = move.piece_moved;
        }

        if (move.en_passant_move)
        {
            const direction = this.white_to_move ? 1 : -1;

            this.board[move.end[0] + direction][move.end[1]] = "--";
        }

        if (move.castle_move)
        {
            const offset1 = (move.end[1] == 2) ?  1 : -1;
            const offset2 = (move.end[1] == 2) ? -2 :  1;
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
        if (move.piece_moved == "wK")
        {
            this.white_king_location = move.end;
        }
        else if (move.piece_moved == "bK")
        {
            this.black_king_location = move.end;
        }

        // En passant location update
        if (move.piece_moved == "wP" && move.end[0] == 4)
        {
            this.en_passant_location = [ move.end[0] + 1, move.end[1] ];
        }
        else if (move.piece_moved == "bP" && move.end[0] == 3)
        {
            this.en_passant_location = [ move.end[0] - 1, move.end[1] ];
        }
        else
        {
            this.en_passant_location = [];
        }
    }

    undo_move()
    {
        if (this.move_log.length == 0)
        {
            return;
        }

        const last_move = this.move_log.pop();

        if (last_move.promotion_move)
        {
            const color = this.white_to_move ? "b" : "w";

            this.board[last_move.end[0]][last_move.end[1]] =
                last_move.piece_captured;
            this.board[last_move.start[0]][last_move.start[1]] = color + 'P';
        }
        else if (last_move.en_passant_move)
        {
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;
            this.board[last_move.end[0]][last_move.end[1]] = "--";

            if (this.white_to_move)
            {
                this.board[last_move.end[0] - 1][last_move.end[1]] = "wP";
            }
            else
            {
                this.board[last_move.end[0] + 1][last_move.end[1]] = "bP";
            }
        }
        else if (last_move.castle_move)
        {
            let end_row = this.board[last_move.end[0]];

            end_row[last_move.end[1]] = "--";
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;

            if (last_move.end[1] == 2)
            {
                end_row[last_move.end[1] - 2] = end_row[last_move.end[1] + 1];
                end_row[last_move.end[1] + 1] = "--";
            }
            else
            {
                end_row[last_move.end[1] + 1] = end_row[last_move.end[1] - 1];
                end_row[last_move.end[1] - 1] = "--";
            }
        }
        else
        {
            this.board[last_move.end[0]][last_move.end[1]] =
                last_move.piece_captured;
            this.board[last_move.start[0]][last_move.start[1]] =
                last_move.piece_moved;
        }

        // King position
        this.white_to_move = !this.white_to_move;

        if (last_move.piece_moved == "wK")
        {
            this.white_king_location = last_move.start;
        }
        else if (last_move.piece_moved == "bK")
        {
            this.black_king_location = last_move.start;
        }

        // To be able to restore the en passant location
        //    we need to look back at 1 more element
        this.en_passant_location = [];

        if (this.move_log.length > 0)
        {
            const previous_move = this.move_log.at(-1);

            if (previous_move.piece_moved == "wP" && previous_move.end[0] == 4)
            {
                this.en_passant_location =
                    [ previous_move.end[0] + 1, previous_move.end[1] ];
            }
            else if (
                previous_move.piece_moved == "bP" && previous_move.end_row == 3)
            {
                this.en_passant_location =
                    [ previous_move.end[0] - 1, previous_move.end[1] ];
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
    get_valid_moves()
    {
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

        if (this.in_check)
        {
            if (this.checks.length == 1)
            {
                const check = this.checks[0];
                const check_piece =
                    this.board[check.location[0]][check.location[1]];
                let valid_squares = [];

                moves = this.get_all_possible_moves();

                if (check_piece[1] == "N")
                {
                    valid_squares = [ check.location ];
                }
                else
                {
                    for (let i = 1; i < 8; ++i)
                    {
                        const valid_square =
                        [
                            king_row + check.direction[0] * i,
                            king_column + check.direction[1] * i
                        ];

                        valid_squares.push(valid_square);

                        if (
                            valid_square[0] == check.location[0] &&
                            valid_square[1] == check.location[1])
                        {
                            break;
                        }
                    }
                }

                for (let i = moves.length - 1; i > -1; --i)
                {
                    if (moves[i].piece_moved[1] != "K")
                    {
                        let found = false;

                        for (const valid_square of valid_squares)
                        {
                            if (
                                valid_square[0] == moves[i].end[0] &&
                                valid_square[1] == moves[i].end[1])
                            {
                                found = true;
                                break;
                            }
                        }

                        if (!found)
                        {
                            moves.splice(i, 1);
                        }
                    }
                }
            }
            // Double check
            else
            {
                this.get_king_moves(king_row, king_column, moves);
            }
        }
        else
        {
            moves = this.get_all_possible_moves();
        }

        if (moves.length == 0)
        {
            if (this.in_check)
            {
                this.checkmate = true;
            }
            else
            {
                this.stalemate = true;
            }
        }

        return moves;
    }

    // All moves without considering checks
    get_all_possible_moves()
    {
        let moves = [];

        for (let row = 0; row < this.board.length; ++row)
        {
            for (let column = 0; column < this.board[row].length; ++column)
            {
                let player = this.board[row][column][0];
                let current_color = this.white_to_move ? "w" : "b";

                if (player == current_color)
                {
                    let piece = this.board[row][column][1];

                    this.move_methods[piece].call(this, row, column, moves);
                }
            }
        }

        return moves;
    }

    get_pins_checks()
    {
        let pins = [];
        let checks = [];
        let in_check = false;

        let king_row;
        let king_column;
        let actor_color;
        let enemy_color;

        if (this.white_to_move)
        {
            king_row = this.white_king_location[0];
            king_column = this.white_king_location[1];
            actor_color = "w";
            enemy_color = "b";
        }
        else
        {
            king_row = this.black_king_location[0];
            king_column = this.black_king_location[1];
            actor_color = "b";
            enemy_color = "w";
        }

        const directions =
        [
            [-1,  0],
            [ 0, -1],
            [ 1,  0],
            [ 0,  1],
            [-1, -1],
            [-1,  1],
            [ 1, -1],
            [ 1,  1]
        ];

        for (let i = 0; i < directions.length; ++i)
        {
            const direction = directions[i];
            let possible_pin = null;

            for (let j = 1; j < 8; ++j)
            {
                const test_row = king_row + direction[0] * j;
                const test_column = king_column + direction[1] * j;

                // Off the board
                if (!check_indices(test_row, test_column))
                {
                    break;
                }

                const end_piece = this.board[test_row][test_column];

                if (end_piece[0] == actor_color)
                {
                    if (possible_pin == null)
                    {
                        possible_pin =
                        {
                            location: [ test_row, test_column ],
                            direction: direction
                        };
                    }
                    else
                    {
                        // More than one piece blocking so it's not a pin
                        break;
                    }
                }
                else if (end_piece[0] == enemy_color)
                {
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

                    if (rook || bishop || pawn || queen || king)
                    {
                        // No piece blocking so check
                        if (possible_pin == null)
                        {
                            in_check = true;

                            checks.push(
                            {
                                location: [ test_row, test_column ],
                                direction: direction
                            });

                            break
                        }
                        // Allied piece blocking so pin
                        else
                        {
                            pins.push(possible_pin);
                            break;
                        }
                    }
                    // No check
                    else
                    {
                        break;
                    }
                }
            }
        }

        for (const direction of this.knight_offsets)
        {
            const test_row = king_row + direction[0];
            const test_column = king_column + direction[1];

            if (!check_indices(test_row, test_column))
            {
                continue;
            }

            const piece = this.board[test_row][test_column];

            if (piece == enemy_color + "N")
            {
                in_check = true;

                checks.push(
                {
                    location: [ test_row, test_column ],
                    direction: direction
                });
            }
        }

        return { in_check: in_check, pins: pins, checks: checks };
    }

    get_pin_state(row, column)
    {
        for (let i = this.pins.length - 1; i > -1; --i)
        {
            const location = this.pins[i].location;

            if (location[0] == row && location[1] == column)
            {
                const pin = this.pins[i];
                const direction = [ pin.direction[0], pin.direction[1] ];

                this.pins.splice(i, 1);

                return { direction: direction, pinned: true };
            }
        }

        return { direction: [], pinned: false };
    }

    get_pawn_moves(row, column, moves)
    {
        const pin_state = this.get_pin_state(row, column);
        const y = (this.white_to_move ? -1 : 1);
        const front_empty = this.board[row + y][column] == "--";

        if (front_empty && check_direction(pin_state, [y, 0]))
        {
            moves.push(
                new Move([ row, column ], [ row + y, column ], this.board));

            const initial_row = (this.white_to_move ? 6 : 1);

            if (row == initial_row && this.board[row + 2 * y][column] == "--")
            {
                moves.push(
                    new Move(
                        [ row, column ], [ row + 2 * y, column ], this.board));
            }
        }

        let x_directions = [-1, 1];

        for (const x of x_directions)
        {
            const enemy_color = (this.white_to_move ? "b" : "w");

            if (column + x < 0 || column + x > 7)
            {
                continue;
            }

            if (!check_direction(pin_state, [y, x]))
            {
                continue;
            }

            if (this.board[row + y][column + x][0] == enemy_color)
            {
                moves.push(
                    new Move(
                        [ row, column ], [ row + y, column + x ], this.board));
            }
            else if (
                this.en_passant_location[0] == row + y &&
                this.en_passant_location[1] == column + x)
            {
                moves.push(
                    new Move(
                        [ row, column ],
                        [ row + y, column + x ],
                        this.board,
                        true));
            }
        }
    }

    find_all_moves(row, column, moves, directions, one_step = false)
    {
        const pin_state = this.get_pin_state(row, column);
        const color = this.white_to_move ? "b" : "w";

        for (const direction of directions)
        {
            if (!check_double_direction(pin_state, direction))
            {
                continue;
            }

            let current_row = row + direction[0];
            let current_column = column + direction[1];
            let blocked = !check_indices(current_row, current_column);

            while (!blocked)
            {
                let push_new = false;

                if (this.board[current_row][current_column] == "--")
                {
                    push_new = true;
                }
                else
                {
                    blocked = true;

                    if (this.board[current_row][current_column][0] == color)
                    {
                        push_new = true;
                    }
                }

                if (push_new)
                {
                    moves.push(
                        new Move(
                            [ row, column ],
                            [ current_row, current_column ],
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

    get_rook_moves(row, column, moves)
    {
        this.find_all_moves(row, column, moves, this.rook_moves);
    }

    get_bishop_moves(row, column, moves)
    {
        this.find_all_moves(row, column, moves, this.bishop_moves);
    }

    get_queen_moves(row, column, moves)
    {
        this.find_all_moves(row, column, moves, this.all_directions);
    }

    get_knight_moves(row, column, moves)
    {
        this.find_all_moves(row, column, moves, this.knight_offsets, true);
    }

    get_king_moves(row, column, moves)
    {
        const enemy_color = this.white_to_move ? "b" : "w";

        this.get_castle_moves(row, column, moves);

        for (const direction of this.all_directions)
        {
            const current_row = row + direction[0];
            const current_column = column + direction[1];
            let pin_checks_result = {};
            let king_location =
                this.white_to_move ?
                this.white_king_location :
                this.black_king_location;

            if (!check_indices(current_row, current_column))
            {
                continue;
            }

            king_location[0] = current_row;
            king_location[1] = current_column;
            pin_checks_result = this.get_pins_checks();
            king_location[0] = row;
            king_location[1] = column;

            if (!pin_checks_result.in_check)
            {
                const current_square = this.board[current_row][current_column];

                if (current_square == "--" || current_square[0] == enemy_color)
                {
                    moves.push(
                        new Move(
                            [ row, column ],
                            [ current_row, current_column ],
                            this.board));
                }
            }
        }
    }

    get_castle_side_moves(
        row, column, moves, king_location, direction, square_count)
    {
        for (let i = 1; i <= square_count; ++i)
        {
            if (this.board[row][column + i * direction] != "--")
            {
                return;
            }
        }

        king_location[1] = column + direction;
        let pin_checks_result1 = this.get_pins_checks();
        king_location[1] = column + 2 * direction;
        let pin_checks_result2 = this.get_pins_checks();
        king_location[1] = column;

        if (!pin_checks_result1.in_check && !pin_checks_result2.in_check)
        {
            moves.push(
                new Move(
                    [ row, column ],
                    [ row, column + 2 * direction ],
                    this.board,
                    false,
                    true));
        }
    }

    get_castle_moves(row, column, moves)
    {
        if (this.in_check)
        {
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

        if (white_king_side || black_king_side)
        {
            this.get_castle_side_moves(row, column, moves, king_location, 1, 2);
        }

        if (white_queen_side || black_queen_side)
        {
            this.get_castle_side_moves(
                row, column, moves, king_location, -1, 3);
        }
    }
}

export class Move
{
    constructor(start, end, board, en_passant_move = false, castle_move = false)
    {
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

        const white_promotion = (this.end[0] == 0 && this.piece_moved == "wP");
        const black_promotion = (this.end[0] == 7 && this.piece_moved == "bP");

        if (white_promotion || black_promotion)
        {
            this.promotion_move = true;
        }
    }

    equals(other)
    {
        return this.move_id == other.move_id;
    }
}

class Castle_rights
{
    constructor(
        white_queen_side, white_king_side, black_queen_side, black_king_side)
    {
        this.white_queen_side = white_queen_side;
        this.white_king_side = white_king_side;
        this.black_queen_side = black_queen_side;
        this.black_king_side = black_king_side;
    }
}

function check_direction(pin_state, direction)
{
    const same_direction =
        pin_state.direction[0] == direction[0] &&
        pin_state.direction[1] == direction[1];

    if (!pin_state.pinned || same_direction)
    {
        return true;
    }
    else
    {
        return false;
    }
}

function check_double_direction(pin_state, direction)
{
    const opposite_direction =
        pin_state.direction[0] == -direction[0] &&
        pin_state.direction[1] == -direction[1];

    return check_direction(pin_state, direction) || opposite_direction;
}

function check_indices(row, column)
{
    return (0 <= row && row <= 7 && 0 <= column && column <= 7);
}