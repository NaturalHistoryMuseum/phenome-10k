const SSR = require( 'vue-server-renderer');
const serverBundle = require('./dist/vue-ssr-server-bundle.json');
const clientManifest = require('../static/dist/vue-ssr-client-manifest.json');

const [/*nodeBinary*/, /*entryScript*/, url, defaultJson] = process.argv;
const defaultData = JSON.parse(defaultJson);

const context = { url, defaultData };

const renderer = SSR.createBundleRenderer(serverBundle, { clientManifest });

renderer.renderToString(context).then(
  html => {
    // NB the context object is populated with some utility
    // functions by the vue-loader
    process.stdout.write(
      `${context.renderResourceHints()}
      ${context.renderStyles()}
      ${html}
      <script>window.p10k_defaultData = ${defaultJson};</script>
      ${context.renderScripts()}`
    );
  }
).catch(
  err => {
    console.error(err.stack || err.message);
    process.exit(err.code || 500);
  }
);
