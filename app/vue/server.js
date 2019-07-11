const { Console } = require('console');
const SSR = require( 'vue-server-renderer');
const serverBundle = require('./dist/vue-ssr-server-bundle.json');
const clientManifest = require('../static/dist/vue-ssr-client-manifest.json');

// Override `console` to log everything to stderr, as we'll be expecting markup on stdout
global.console = new Console({ stdout: process.stderr, stderr: process.stderr });

function readJson() {
  return new Promise((res, rej) => {
    let json = '';
    process.stdin.on('data', chunk => json += chunk.toString());
    process.stdin.on('end', a => {
      try {
        res(JSON.parse(json))
      } catch(e) {
        rej(e)
      }
    });
  });
}

const [/*nodeBinary*/, /*entryScript*/, url] = process.argv;

const renderer = SSR.createBundleRenderer(serverBundle, { clientManifest });

readJson().then(async defaultData => {
    const context = { url, defaultData };
    const html = await renderer.renderToString(context);
    // NB the context object is populated with some utility
    // functions by the vue-loader
    process.stdout.write(
      `${context.renderResourceHints()}
      ${context.renderStyles()}
      ${html}
      <script>window.p10k_defaultData = ${JSON.stringify(defaultData)};</script>
      ${context.renderScripts()}`
    );
  }
).catch(
  err => {
    console.error(err.stack || err.message);
    process.exit(err.code || 500);
  }
);
