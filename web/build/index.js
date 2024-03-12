const webpack = require('webpack');
const rimraf = require('rimraf');
const serverConfig = require('./webpack.server.config');
const clientConfig = require('./webpack.client.config');

const compiler = webpack([serverConfig, clientConfig]);

const clear = () => new Promise((res) => rimraf(clientConfig.output.path, res));

module.exports = {
  compiler,
  clear,
};

if (require.main === module) {
  // 1. Remove existing client output directory
  clear().then(() => {
    // 2. Compile server and client bundles
    compiler.run((err, stats) => {
      if (stats) {
        // 3. Report back
        // this callback is called twice; once for
        // client and once for server
        const info = stats.toJson();

        if (stats.hasErrors()) {
          err = info.errors.join('\n');
        }

        if (stats.hasWarnings()) {
          process.stdout.write(info.warnings + '\n');
        }

        process.stdout.write(stats.toString() + '\n');
      }

      if (err) {
        process.exitCode = 1;
        process.stderr.write(err.toString() + '\n');
      }
    });
  });
}
