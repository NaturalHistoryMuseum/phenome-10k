const rpc = require('./rpc');
const makeRender = require('./render');

function app(renderer) {
	const render = makeRender(renderer);

	return rpc({ render });
}

module.exports = app;
