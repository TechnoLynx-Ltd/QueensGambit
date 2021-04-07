import copy
import numpy as np


class GameState:

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.position_dict = {'wP': 0, 'wR': 1, 'wN': 2, 'wB': 3, 'wQ': 4, 'wK': 5,
                              'bP': 6, 'bR': 7, 'bN': 8, 'bB': 9, 'bQ': 10, 'bK': 11}

        self.white_to_move = True
        self.move_log = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.en_passant_loc = ()
        self.cur_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [copy.deepcopy(self.cur_castle_rights)]
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.move_methods = {
            'P': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.board)

    def get_position(self):
        """
        Parse self.board into ndarray of size (8, 8, 12)
        :return position: np.ndarray
        """
        position = np.zeros((8, 8, 12), dtype=np.int8)

        for i, line in enumerate(self.board):
            for j, pos in enumerate(line):
                if pos != "--":
                    position[i, j, self.position_dict[pos]] = 1

        return position

    def update_castle_rights(self, move):
        if self.white_to_move:
            if move.piece_moved == "wK":
                self.cur_castle_rights.wks = False
                self.cur_castle_rights.wqs = False
            elif move.piece_moved == "wR" and move.start_col == 0 and move.start_row == 7:
                self.cur_castle_rights.wqs = False
            elif move.piece_moved == "wR" and move.start_col == 7 and move.start_row == 7:
                self.cur_castle_rights.wks = False
            if move.piece_captured == "bR" and move.end_row == 0:
                if move.end_col == 0:
                    self.cur_castle_rights.bqs = False
                elif move.end_col == 7:
                    self.cur_castle_rights.bks = False
        else:
            if move.piece_moved == "bK":
                self.cur_castle_rights.bks = False
                self.cur_castle_rights.bqs = False
            elif move.piece_moved == "bR" and move.start_col == 0 and move.start_row == 0:
                self.cur_castle_rights.bqs = False
            elif move.piece_moved == "bR" and move.start_col == 7 and move.start_row == 0:
                self.cur_castle_rights.bks = False
            if move.piece_captured == "wR" and move.end_row == 7:
                if move.end_col == 0:
                    self.cur_castle_rights.wqs = False
                elif move.end_col == 7:
                    self.cur_castle_rights.wks = False

    def make_move(self, move):
        # TODO - AttributeError: 'NoneType' object has no attribute 'start_row'
        self.board[move.start_row][move.start_col] = "--"

        if move.promotion_move:
            if self.white_to_move:
                self.board[move.end_row][move.end_col] = "wQ"
            else:
                self.board[move.end_row][move.end_col] = "bQ"
        elif move.en_passant_move:
            self.board[move.end_row][move.end_col] = move.piece_moved
            if self.white_to_move:
                self.board[move.end_row + 1][move.end_col] = "--"
            else:
                self.board[move.end_row - 1][move.end_col] = "--"
        elif move.castle_move:
            self.board[move.end_row][move.end_col] = move.piece_moved
            if move.end_col == 2:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

                self.board[move.end_row][move.end_col - 2] = "--"
            else:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
        else:
            self.board[move.end_row][move.end_col] = move.piece_moved

        # Castle rights update
        self.update_castle_rights(move)
        self.castle_rights_log.append(copy.deepcopy(self.cur_castle_rights))

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # King position
        if move.piece_moved == "wK":
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)

        # En passant location update
        if move.piece_moved == "wP" and move.end_row == 4:
            self.en_passant_loc = (move.end_row + 1, move.end_col)
        elif move.piece_moved == "bP" and move.end_row == 3:
            self.en_passant_loc = (move.end_row - 1, move.end_col)
        else:
            self.en_passant_loc = ()

    def undo_move(self):
        if len(self.move_log) != 0:
            last_move = self.move_log.pop()

            if last_move.promotion_move:
                if self.white_to_move:
                    self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
                    self.board[last_move.start_row][last_move.start_col] = "bP"
                else:
                    self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
                    self.board[last_move.start_row][last_move.start_col] = "wP"
            elif last_move.en_passant_move:
                self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
                self.board[last_move.end_row][last_move.end_col] = "--"
                if self.white_to_move:
                    self.board[last_move.end_row - 1][last_move.end_col] = "wP"
                else:
                    self.board[last_move.end_row + 1][last_move.end_col] = "bP"
            elif last_move.castle_move:
                self.board[last_move.end_row][last_move.end_col] = "--"
                self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
                if last_move.end_col == 2:
                    self.board[last_move.end_row][last_move.end_col - 2] = self.board[last_move.end_row][
                        last_move.end_col + 1]
                    self.board[last_move.end_row][last_move.end_col + 1] = "--"
                else:
                    self.board[last_move.end_row][last_move.end_col + 1] = self.board[last_move.end_row][
                        last_move.end_col - 1]
                    self.board[last_move.end_row][last_move.end_col - 1] = "--"
            else:
                self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
                self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved

            # King position
            self.white_to_move = not self.white_to_move
            if last_move.piece_moved == "wK":
                self.white_king_loc = (last_move.start_row, last_move.start_col)
            elif last_move.piece_moved == "bK":
                self.black_king_loc = (last_move.start_row, last_move.start_col)

            # To be able to restore the en passant location we need to look back at 1 more element
            self.en_passant_loc = ()
            if len(self.move_log) > 0:
                pevious_move = self.move_log[-1]
                if pevious_move.piece_moved == "wP" and pevious_move.end_row == 4:
                    self.en_passant_loc = (pevious_move.end_row + 1, pevious_move.end_col)
                elif pevious_move.piece_moved == "bP" and pevious_move.end_row == 3:
                    self.en_passant_loc = (pevious_move.end_row - 1, pevious_move.end_col)

            # Undo castle rights
            self.castle_rights_log.pop()
            self.cur_castle_rights = copy.deepcopy(self.castle_rights_log[-1])

            # Set checkmate and stalemate to false
            if self.checkmate:
                self.checkmate = False
            if self.stalemate:
                self.stalemate = False

    def get_valid_moves(self):
        """
        All moves considering checks
        """
        moves = []
        self.in_check, self.pins, self.checks = self.get_pins_checks()
        if self.white_to_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]

        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                crow = check[0]
                ccol = check[1]
                cpiece = self.board[crow][ccol]
                valid_squares = []
                if cpiece[1] == "N":
                    valid_squares = [(crow, ccol)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == crow and valid_square[1] == ccol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # double check
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True

        return moves

    def get_all_possible_moves(self):
        """
        Get all moves without considering checks
        """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                player = self.board[r][c][0]
                if (player == 'w' and self.white_to_move) or (player == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_methods[piece](r, c, moves)

        return moves

    def get_pins_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            ecolor = "b"
            acolor = "w"
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            ecolor = "w"
            acolor = "b"
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                trow = king_row + d[0] * i
                tcol = king_col + d[1] * i
                if 0 <= trow < 8 and 0 <= tcol < 8:
                    end_piece = self.board[trow][tcol]
                    if end_piece[0] == acolor and end_piece[1] != "K":
                        if possible_pin == ():
                            possible_pin = (trow, tcol, d[0], d[1])
                        else:
                            break  # at least more than one piece blocking so it's not a pin
                    elif end_piece[0] == ecolor:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "P" and (
                                        (ecolor == "w" and 6 <= j <= 7) or (ecolor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possible_pin == ():  # no piece blocking so check
                                in_check = True
                                checks.append((trow, tcol, d[0], d[1]))
                                break
                            else:  # allied piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # no check
                            break
                else:  # off the board
                    break
        knight_offsets = ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, -1), (-2, 1))
        for offset in knight_offsets:
            trow = king_row + offset[0]
            tcol = king_col + offset[1]
            if 0 <= trow <= 7 and 0 <= tcol <= 7:
                piece = self.board[trow][tcol]
                if piece[0] == ecolor and piece[1] == "N":
                    in_check = True
                    checks.append((trow, tcol, offset[0], offset[1]))
        return in_check, pins, checks

    def get_pin_state(self, r, c):
        pin_dir = ()
        pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                return pin_dir, pinned
        return pin_dir, pinned

    def get_pawn_moves(self, r, c, moves):
        pin_dir, pinned = self.get_pin_state(r, c)

        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                if not pinned or pin_dir == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if not pinned or pin_dir == (-1, -1):
                    if self.board[r - 1][c - 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif self.en_passant_loc == (r - 1, c - 1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, en_passant_move=True))
            if c + 1 <= 7:
                if not pinned or pin_dir == (-1, 1):
                    if self.board[r - 1][c + 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif self.en_passant_loc == (r - 1, c + 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, en_passant_move=True))
        else:
            if self.board[r + 1][c] == "--":
                if not pinned or pin_dir == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if not pinned or pin_dir == (1, 1):
                    if self.board[r + 1][c - 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif self.en_passant_loc == (r + 1, c - 1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, en_passant_move=True))
            if c + 1 <= 7:
                if not pinned or pin_dir == (1, -1):
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif self.en_passant_loc == (r + 1, c + 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, en_passant_move=True))

    def get_rook_moves(self, r, c, moves):
        pin_dir, pinned = self.get_pin_state(r, c)
        color = "b" if self.white_to_move else "w"
        for dir in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if not pinned or dir == pin_dir or dir == (-pin_dir[0], -pin_dir[1]):
                blocked = False
                i = dir[0]
                j = dir[1]
                rp = r
                cp = c
                while not blocked and 0 <= cp + j <= 7 and 0 <= rp + i <= 7:
                    rp = rp + i
                    cp = cp + j
                    if self.board[rp][cp] == "--":
                        moves.append(Move((r, c), (rp, cp), self.board))
                    else:
                        blocked = True
                        if self.board[rp][cp][0] == color:
                            moves.append(Move((r, c), (rp, cp), self.board))

    def get_knight_moves(self, r, c, moves):
        _, pinned = self.get_pin_state(r, c)
        color = "b" if self.white_to_move else "w"
        for dir in [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)]:
            rp = r + dir[0]
            cp = c + dir[1]
            if not pinned:
                if 7 >= rp >= 0 and 7 >= cp >= 0:
                    destination = self.board[rp][cp]
                    if destination[0] == color or destination == "--":
                        moves.append(Move((r, c), (rp, cp), self.board))

    def get_bishop_moves(self, r, c, moves):
        pin_dir, pinned = self.get_pin_state(r, c)
        color = "b" if self.white_to_move else "w"
        for dir in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if not pinned or dir == pin_dir or dir == (-pin_dir[0], -pin_dir[1]):
                blocked = False
                i = dir[0]
                j = dir[1]
                rp = r
                cp = c
                while not blocked and 0 <= cp + j <= 7 and 0 <= rp + i <= 7:
                    rp = rp + i
                    cp = cp + j
                    if self.board[rp][cp] == "--":
                        moves.append(Move((r, c), (rp, cp), self.board))
                    else:
                        blocked = True
                        if self.board[rp][cp][0] == color:
                            moves.append(Move((r, c), (rp, cp), self.board))

    def get_queen_moves(self, r, c, moves):
        pin_dir, pinned = self.get_pin_state(r, c)
        color = "b" if self.white_to_move else "w"
        for dir in [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            if not pinned or dir == pin_dir or dir == (-pin_dir[0], -pin_dir[1]):
                blocked = False
                i = dir[0]
                j = dir[1]
                rp = r
                cp = c
                while not blocked and 0 <= cp + j <= 7 and 0 <= rp + i <= 7:
                    rp = rp + i
                    cp = cp + j
                    if self.board[rp][cp] == "--":
                        moves.append(Move((r, c), (rp, cp), self.board))
                    else:
                        blocked = True
                        if self.board[rp][cp][0] == color:
                            moves.append(Move((r, c), (rp, cp), self.board))

    def get_king_moves(self, r, c, moves):
        color = "b" if self.white_to_move else "w"
        for dir in [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            i = dir[0]
            j = dir[1]
            rp = r
            cp = c
            if 0 <= cp + j <= 7 and 0 <= rp + i <= 7:
                rp = rp + i
                cp = cp + j
                if self.white_to_move:
                    self.white_king_loc = (rp, cp)
                    will_be_in_check, _, _ = self.get_pins_checks()
                    self.white_king_loc = (r, c)
                else:
                    self.black_king_loc = (rp, cp)
                    will_be_in_check, _, _ = self.get_pins_checks()
                    self.black_king_loc = (r, c)
                if not will_be_in_check:
                    if self.board[rp][cp] == "--" or self.board[rp][cp][0] == color:
                        moves.append(Move((r, c), (rp, cp), self.board))
        self.get_castle_moves(r, c, moves)

    def get_castle_moves(self, r, c, moves):
        if self.in_check:
            return
        if (self.white_to_move and self.cur_castle_rights.wks) or (
                not self.white_to_move and self.cur_castle_rights.bks):
            self.get_ks_castle_moves(r, c, moves)
        if (self.white_to_move and self.cur_castle_rights.wqs) or (
                not self.white_to_move and self.cur_castle_rights.bqs):
            self.get_qs_castle_moves(r, c, moves)

    def get_ks_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if self.white_to_move:
                self.white_king_loc = (r, c + 1)
                will_be_in_check1, _, _ = self.get_pins_checks()
                self.white_king_loc = (r, c + 2)
                will_be_in_check2, _, _ = self.get_pins_checks()
                self.white_king_loc = (r, c)
                if not will_be_in_check1 and not will_be_in_check2:
                    moves.append(Move((r, c), (r, c + 2), self.board, castle_move=True))
            else:
                self.black_king_loc = (r, c + 1)
                will_be_in_check1, _, _ = self.get_pins_checks()
                self.black_king_loc = (r, c + 2)
                will_be_in_check2, _, _ = self.get_pins_checks()
                self.black_king_loc = (r, c)
                if not will_be_in_check1 and not will_be_in_check2:
                    moves.append(Move((r, c), (r, c + 2), self.board, castle_move=True))

    def get_qs_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if self.white_to_move:
                self.white_king_loc = (r, c - 1)
                will_be_in_check1, _, _ = self.get_pins_checks()
                self.white_king_loc = (r, c - 2)
                will_be_in_check2, _, _ = self.get_pins_checks()
                self.white_king_loc = (r, c)
                if not will_be_in_check1 and not will_be_in_check2:
                    moves.append(Move((r, c), (r, c - 2), self.board, castle_move=True))
            else:
                self.black_king_loc = (r, c - 1)
                will_be_in_check1, _, _ = self.get_pins_checks()
                self.black_king_loc = (r, c - 2)
                will_be_in_check2, _, _ = self.get_pins_checks()
                self.black_king_loc = (r, c)
                if not will_be_in_check1 and not will_be_in_check2:
                    moves.append(Move((r, c), (r, c - 2), self.board, castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks,
        self.wqs = wqs,
        self.bqs = bqs


class Move:
    rank_to_row = {'1': 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    row_to_rank = {v: k for k, v in rank_to_row.items()}
    file_to_col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_file = {v: k for k, v in file_to_col.items()}

    def __init__(self, start, end, board, en_passant_move=False, castle_move=False):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.promotion_move = False
        if self.end_row == 0 and self.piece_moved == "wP":
            self.promotion_move = True
        elif self.end_row == 7 and self.piece_moved == "bP":
            self.promotion_move = True
        self.en_passant_move = en_passant_move
        self.castle_move = castle_move

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.col_to_file[col] + self.row_to_rank[row]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
