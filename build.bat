pip install -r src/requirements.txt
cd src/model
py train_model.py
cd ../..
call npm install
tensorflowjs_converter ^
    --input_format tfjs_layers_model ^
    --output_format tfjs_graph_model ^
    saved_model_js/model.json ^
    graph_model_js/
call npx tfjs-custom-module --config custom_tfjs_config.json
call npx webpack
echo.
echo.
echo If there were no errors, the bundled index file is in resources/html/dist/