from engine import GameState
import ai
import numpy as np
from tensorflow import keras
import random



class ModelTournament:
    def __init__ (self, name_find_move:dict, num_games=100):
        self.name_find_move = name_find_move
        self.game_results = {name: [0,0,0] for name in name_find_move}
        self.num_games = num_games

    def play_tournament(self):
        
        model_names = list(self.name_find_move.keys())
        for model in model_names:
            #curent model always plays as white and enemy is black
            enemies = [model_name for model_name in model_names if model_name!=model]
            for enemy in enemies:
                gs = GameState()
                move_count = 0
                valid_moves = gs.get_valid_moves()
                random.shuffle(valid_moves)
                played_games = 0
                while played_games < 1:
                    while not gs.checkmate and not gs.stalemate and move_count<500:
                        print(gs)
                        move_count += 1
                        if gs.white_to_move:
                            chosen_move = self.name_find_move[model](gs, valid_moves)
                        else:
                            chosen_move = self.name_find_move[enemy](gs, valid_moves)
                        gs.make_move(chosen_move)
                        valid_moves = gs.get_valid_moves()
                        random.shuffle(valid_moves)

                    if move_count >= 500:
                        game_result = [0,1,0]
                        self.game_results[model] =[self.game_results[model][i]+game_result[i] for i in range(3)]
                        self.game_results[enemy] =[self.game_results[enemy][i]+game_result[::-1][i] for i in range(3)]


                    played_games += 1
                    if gs.checkmate:
                        if gs.white_to_move:
                            game_result = [0,0,1]
                            self.game_results[model] =[self.game_results[model][i]+game_result[i] for i in range(3)]
                            self.game_results[enemy] =[self.game_results[enemy][i]+game_result[::-1][i] for i in range(3)]
                        else:
                            game_result = [1,0,0]
                            self.game_results[model] =[self.game_results[model][i]+game_result[i] for i in range(3)]
                            self.game_results[enemy] =[self.game_results[enemy][i]+game_result[::-1][i] for i in range(3)]
                            
                    else:
                        game_result = [0,1,0]
                        self.game_results[model] =[self.game_results[model][i]+game_result[i] for i in range(3)]
                        self.game_results[enemy] =[self.game_results[enemy][i]+game_result[::-1][i] for i in range(3)]

        return self.game_results
    
    def rank_models(self):
        model_names = list(self.name_find_move.keys())
        model_names.sort(key=lambda x: self.game_results[x], reverse=True)
        print("Rating from best to worst:")
        for model_name in model_names:
            print(f'{model_name} with the result {self.game_results[model_name]}')
        return model_names


#For model ranking
if __name__ == "__main__":
    model = keras.models.load_model('../model')
    def find_model_move(gs, valid_moves):
        return ai.find_model_best_move_without_scoring(gs, valid_moves, model)
    def find_minmax_best_move_1(gs, valid_moves):
        return ai.find_minmax_best_move(gs, valid_moves, depth=1)
    tournament = ModelTournament({"ANN": find_model_move, "MinMax depth 1":find_minmax_best_move_1, "MinMax depth 2":ai.find_minmax_best_move})
    result = tournament.play_tournament()
    tournament.rank_models()

