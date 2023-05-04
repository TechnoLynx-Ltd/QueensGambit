from engine import GameState
import ai
import numpy as np
from tensorflow import keras
import random
import chess

class ModelsGame:

    def __init__ (self, find_white_move, find_black_move, num_games = 1000, black_model_name = None, white_model_name = None):
        self.find_white_move = find_white_move
        self.find_black_move = find_black_move
        self.num_games = num_games
        self.white_model_name = white_model_name
        self.black_model_name = black_model_name
        self.white_wins = 0
        self.black_wins = 0
        self.stalemates = 0
    
    def generate_random_gs(self):
        gs_fen = GameState(randomize=True).get_fen()
        return gs_fen


    def play_random_game(self):
        
        positions = []
        moves = []
        results = []
        white_move = []
        played_games = 0

        while played_games < self.num_games: 
            print(f'{self.white_model_name} and {self.black_model_name} played {played_games} games')
            gs = chess.Board(fen=self.generate_random_gs())
            move_count = 0
            this_game_positions = []
            this_game_white_move = []
            valid_moves = gs.legal_moves
            random.shuffle(list(valid_moves))
            while not gs.is_game_over() and move_count<300:
                # print(gs)
                this_game_positions.append(gs.fen())
                this_game_white_move.append(gs.turn == chess.WHITE)
                move_count += 1
                if gs.turn == chess.WHITE:
                    chosen_move = self.find_white_move(gs, valid_moves)
                else:
                    chosen_move = self.find_black_move(gs, valid_moves)
                gs.push(chosen_move)
                valid_moves = gs.legal_moves
                random.shuffle(list(valid_moves))

            this_game_positions.append(gs.fen().split(' ')[0])
            this_game_white_move.append(gs.turn == chess.WHITE)
            if move_count >= 300:
                continue

            played_games += 1
            if gs.is_checkmate():
                if gs.turn == chess.WHITE:
                    game_result = [0,0,1]
                    self.black_wins += 1
                else:
                    game_result = [1,0,0]
                    self.white_wins += 1
            else:
                game_result = [0,1,0]
                self.stalemates += 1

            for i in range(move_count, -1, -1):
                    moves.append(i)
                    results.append(game_result)
            positions += this_game_positions
            white_move += this_game_white_move
        positions = np.array(positions)
        moves = np.array(moves).astype(np.uint8)
        results = np.array(results)
        white_move = np.array(white_move).astype(np.uint8)
        print(f'Moves: {moves.shape}')
        print(f'Positions: {positions.shape}')
        print(f'Result: {results.shape}')
        print(f'White moves: {white_move.shape}')
        return positions, moves, results, white_move

    def save_res(self, X_position, y_moves, y_result, X_white_move, folder="data_sim_bitboard_less_random"):
        # positions = np.load(f"../../{folder}/npy/fen_bitboards.npy")
        # moves = np.load(f"../../{folder}/npy/y_moves.npy").astype(np.int8) 
        # result = np.load(f"../../{folder}/npy/y_result.npy").astype(np.int8)
        # white_move = np.load(f"../../{folder}/npy/X_white_move.npy").astype(np.int8)
        # X_position = np.append(X_position, positions, axis=0)
        # y_moves = np.append(y_moves, moves, axis=0)
        # y_result = np.append(y_result, result, axis=0)
        # X_white_move = np.append(X_white_move, white_move, axis=0)
        print(X_white_move.shape)
        print("Saving dataset to file")
        with open(f"../../{folder}/npy/fen_bitboards.npy", 'wb') as X_pos_file:
            np.save(X_pos_file, X_position)
        with open(f"../../{folder}/npy/X_white_move.npy", "wb") as y_res_file:
            np.save(y_res_file, X_white_move)
        with open(f"../../{folder}/npy/y_moves.npy", "wb") as y_res_file:
            np.save(y_res_file, y_moves)
        with open(f"../../{folder}/npy/y_result.npy", "wb") as y_res_file:
            np.save(y_res_file, y_result)
        return X_position, X_white_move, y_moves, y_result

    def record_stats(self, loggs_file='./tournaments_results.txt'):
        with open(loggs_file, 'w') as stats_file:
            stats_file.write(f"{self.white_model_name}: {self.white_wins}, {self.black_model_name}: {self.black_wins}, stalemates: {self.stalemates}\n")
        return self.white_wins, self.stalemates, self.black_wins

if __name__ == "__main__":
    # model = keras.models.load_model('../model')
    # def find_model_move(gs, valid_moves):
    #     return ai.find_model_best_move_without_scoring(gs, valid_moves, model)
    def find_minmax_best_move_1(gs, valid_moves):
        return ai.find_minmax_best_move_bitboard(gs, valid_moves, depth=1)
    def find_minmax_best_move_3(gs, valid_moves):
        return ai.find_minmax_best_move_bitboard(gs, valid_moves, depth=3)
    algorithms = {"MinMax depth 3":find_minmax_best_move_3, "MinMax depth 2":ai.find_minmax_best_move_bitboard}
    algorithms_names = list(algorithms.keys())
    for algorithm in algorithms:
        enemies = [model_name for model_name in algorithms_names if model_name!=algorithm]
        for enemy in enemies:
            game = ModelsGame(algorithms[algorithm], algorithms[enemy], 3000, enemy, algorithm)
            res = game.play_random_game()
            game.save_res(res[0], res[1], res[2], res[3])
    # positions = np.load(f"../../data_sim_bitboard_real_game/npy/fen_bitboards.npy")
    # print(positions.shape)