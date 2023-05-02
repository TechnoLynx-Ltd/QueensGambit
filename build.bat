mkdir data\npy
cd python/data_process
py pgn_dataset.py
cd ../..
pip install -r python/requirements.txt
cd python/model
py train_model.py
cd ../../website
call npm install
tensorflowjs_converter ^
    --input_format tfjs_layers_model ^
    --output_format tfjs_graph_model ^
    ../saved_model_js/model.json ^
    graph_model_js/
call npx tfjs-custom-module --config custom_tfjs_config.json
call npx webpack
cd ..
echo.
echo.
echo If there were no errors, the bundled index file is in website/dist/