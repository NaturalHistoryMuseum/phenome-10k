const path = require('path');
const merge = require('webpack-merge');
const baseConfig = require('./webpack.base.config.js');
const VueSSRClientPlugin = require('vue-server-renderer/client-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = merge(baseConfig, {
  entry: './node/src/entry-client.js',
  output: {
    path: path.resolve('../static/dist'),
    publicPath: '/static/dist/',
  },
  plugins: [
    // This plugins generates `vue-ssr-client-manifest.json` in the
    // output directory.
    new VueSSRClientPlugin(),
    new MiniCssExtractPlugin(),
  ],
  module: {
    rules: [
      {
        test: /\.s?css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: { modules: true, localIdentName: '[name]__[local]' },
          },
          'sass-loader',
        ],
      },
    ],
  },
  // Important: this splits the webpack runtime into a leading chunk
  // so that async chunks can be injected right after it.
  // this also enables better caching for your app/vendor code.
  optimization: {
    runtimeChunk: {
      name: 'manifest',
    },
  },
});
