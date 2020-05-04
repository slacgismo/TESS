const path = require('path');
const webpack = require("webpack");

module.exports = {
    watchOptions: {
        ignored: /node_modules/
    },
    entry: {
        main: "./static/js/base.js",
        auth: "./auth/static/auth.js",
        alerts: "./alerts/static/alerts.js",
        constraints: "./constraints/static/constraints.js",
        cost_revenue: "./cost_revenue/static/cost_revenue.js",
        markets: "./markets/static/markets.js",
        notifications: "./notifications/static/notifications.js",
        user_settings: "./user_settings/static/user_settings.js",
        storage: "./power_dispatch/static/storage.js",
        capacity: "./power_dispatch/static/capacity.js"
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
