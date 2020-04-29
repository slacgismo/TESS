const path = require('path');
const webpack = require("webpack");

module.exports = {
    watchOptions: {
        ignored: /node_modules/
    },
    entry: {
        main: "./static/base.js",
        auth: "./auth/static/auth.js"
    },
    output: {
        path: __dirname + '/static/bundles',
        filename: '[name].bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ["@babel/preset-env", "@babel/preset-react"]
                }                
            },
            {
                test: /\.css$/,
                // exclude material css from being loaded by CSS modules
                // These paths are specific to your system, so change accordingly
                exclude: [
                    path.resolve('./node_modules/material-components-web'),
                    path.resolve('./node_modules/@material')
                ],
                use: ['style-loader', 'css-loader?modules=true']
            },
            {
                test: /\.css$/,
                // only turn on standard global CSS loader for the material directories
                // These paths are the same as above and specific to your system, so change accordingly
                include: [
                    path.resolve('./node_modules/material-components-web'),
                    path.resolve('./node_modules/@material')
                ],
                use: ['style-loader', 'css-loader']
            }   
        ]
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin()
    ]
};
