const path = require('path');

module.exports = {
  entry: './src/javascripts/jsx/run.js',
  output: {
    path: path.resolve(__dirname, 'app/app/static/js'),
    filename: 'run.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      }
    ]
  }
};
