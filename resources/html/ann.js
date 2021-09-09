let model = null;

async function load_model()
{
    model = await tf.loadLayersModel("../../saved_model_js/model.json");
    console.log("Model loaded");
    console.log(model.summary());
}

function find_model_best_move(game_state, valid_moves)
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