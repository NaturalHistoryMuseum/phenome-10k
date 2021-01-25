#!/usr/bin/env node

const SSR = require('vue-server-renderer');
const serverBundle = require('./dist/vue-ssr-server-bundle.json');
const clientManifest = require('../app/static/dist/vue-ssr-client-manifest.json');
const renderer = SSR.createBundleRenderer(serverBundle, { clientManifest });
const argv = require('yargs/yargs')(process.argv.slice(2)).argv;

const server = require('./server').admin;

module.exports = server(renderer);

const bind = argv.bind || '127.0.0.1:8080';
const [ip, port] = bind.split(':');

require('simple-wsgi')(module.exports, port || process.env.PORT || 8080, ip || '127.0.0.1');
