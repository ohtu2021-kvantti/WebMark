const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const {WebpackManifestPlugin} = require('webpack-manifest-plugin');

module.exports = {
  entry: {
    index: './static/js/index.js',
    compareAlgorithms: './static/js/compareAlgorithms.js',
  },
  plugins: [
      new CleanWebpackPlugin(),  
      new WebpackManifestPlugin(), 
  ],
  output: {
    publicPath: '',
    filename: '[name].[contenthash].js', 
    path: path.resolve(__dirname, 'build'),
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
          options: {
            presets: [
              [
                '@babel/preset-env',
                {
                  "useBuiltIns": "entry",
                  "corejs": "3.9"
                }
              ]
            ]
          }
      },
    ],
  },
};