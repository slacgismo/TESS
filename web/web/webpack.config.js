const webpack = require("webpack");

module.exports = {  
    entry: {
        main: "./static/index.js",
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
            }   
        ]
    },
    plugins: [new webpack.HotModuleReplacementPlugin()]
};
