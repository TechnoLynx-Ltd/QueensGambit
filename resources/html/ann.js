import * as tf from "@tensorflow/tfjs";

import model_config_json from "../../saved_model_js/model.json";
import model_weights from "../../saved_model_js/group1-shard1of1.bin";
import { Inline_model_handler } from "./Inline_model_handler";

let model = null;

export async function load_model()
{
    // cut off the format identifier ("data:application/octet-stream;base64,")
    model_weights = model_weights.substring(37);
    model =
        await tf.loadLayersModel(
            new Inline_model_handler(model_config_json, model_weights));
}

export function find_model_best_move(game_state, valid_moves)
{
    let max_score = 0;
    let next_move = null;

    if (!model)
    {
        return next_move;
    }

    for (const move of valid_moves)
    {
        let scores;
        let score;

        // Make a valid move
        game_state.make_move(move);

        // Expand current position to 4D b/c model input requirement
        const input = tf.tensor([ game_state.get_position() ]);

        // Model predicts score (shape:(1,2)) of current position
        scores = model.predict(input).arraySync();
        console.assert(scores[0][0] + scores[0][1] >= 0.99);

        // White score: 0, Black score: 1
        score = scores[0][game_state.white_to_move ? 0 : 1];

        if (score > max_score)
        {
            max_score = score;
            next_move = move;
        }

        // Restore game_state into original position
        game_state.undo_move();
    }

    return next_move;
}