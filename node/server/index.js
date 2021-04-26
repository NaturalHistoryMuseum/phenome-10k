const rpc = require('./rpc');
const makeRender = require('./render');
const views = import('./views/index.js').then(m=>m.default);

async function app(renderer) {
	const render = makeRender(renderer);

	return rpc({
		render,
		views: await views
	});
}

module.exports = app;
