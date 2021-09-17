const HtmlWebpackPlugin = require("html-webpack-plugin");
const HtmlInlineScriptPlugin = require('html-inline-script-webpack-plugin');
const path = require("path");

module.exports = {
    devServer:
    {
        static: "./resources/html/dist",
    },
    entry: "./resources/html/index.js",
    module:
    {
        rules:
        [
            {
                test: /\.(png|svg|jpg|jpeg|gif|bin)$/i,
                type: "asset/inline",
            },
            {
                test: /\.json$/i,
                type: "asset/source",
            },
            {
                test: /\.tsx?$/,
                use: "ts-loader",
                exclude: /node_modules/,
            },
        ],
    },
    output:
    {
        clean: true,
        filename: "main.js",
        library: "index",
        path: path.resolve(__dirname, "./resources/html/dist"),
        publicPath: "",
    },
    plugins:
    [
        new HtmlWebpackPlugin(
        {
            template: "./resources/html/index.html",
            inject: "head",
        }),
        new HtmlInlineScriptPlugin(),
    ],
    resolve:
    {
        extensions: ['.tsx', '.ts', '.js'],
    },
};