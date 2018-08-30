const path = require('path');
const webpack = require('webpack')

module.exports = {
  mode: "development",
  entry: {
    pageRun: './src/javascripts/run.jsx',
  },
  output: {
    path: path.resolve(__dirname, 'app/app/static/js'),
    filename: '[name].js'
  },
  module: {
    rules: [{
      test: /\.(js|jsx)$/,
      exclude: /node_modules/,
      use: {
        loader: "babel-loader",
        options: {
          presets: ['@babel/preset-env', '@babel/preset-react']
        }
      }
    }]
  },
  plugins: [
    new webpack.ProgressPlugin(),
  ]
};
