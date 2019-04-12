const path = require('path')
const merge = require('webpack-merge')
const baseConfig = require('./webpack.base.config.js')
const VueSSRClientPlugin = require('vue-server-renderer/client-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = merge(baseConfig, {
  entry: './app/vue/src/entry-client.js',
  output: {
    path: path.resolve('./app/static/dist'),
    publicPath: '/static/dist/'
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
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader',
        ]
      },
      {
        test: /jsc3d/, // Special shim for the jsc3d modules, as they're too old to use any recognised module system
        use: [
          'expose-loader?JSC3D',               // 3. Set window.JSC3D to be the exported object
          'exports-loader?JSC3D',              // 2. Export the JSC3D object from the module
          'imports-loader?JSC3D=>window.JSC3D' // 1. Pass the global JSC3D object to the module (if it's defined)
        ]
      }
    ]
  },
  // Important: this splits the webpack runtime into a leading chunk
  // so that async chunks can be injected right after it.
  // this also enables better caching for your app/vendor code.
  optimization: {
    runtimeChunk: {
      name: 'manifest'
    }
  }
})
