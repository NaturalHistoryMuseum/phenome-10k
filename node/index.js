#!/usr/bin/env node

const SSR = require('vue-server-renderer');
const serverBundle = require('./dist/vue-ssr-server-bundle.json');
const clientManifest = require('../static/dist/vue-ssr-client-manifest.json');
const renderer = SSR.createBundleRenderer(serverBundle, {
	runInNewContext: false,
	clientManifest
});
const argv = require('yargs/yargs')(process.argv.slice(2)).argv;

const server = require('./server');

const bind = argv.bind || '127.0.0.1:8080';
const [ip, port] = bind.split(':');

const start = require('simple-wsgi');

server(renderer).then(
	app => {
		start(app, port || process.env.PORT || 8080, ip || '127.0.0.1');
	},
	e => {
		console.error(e);
		process.exit(1);
	}
)
