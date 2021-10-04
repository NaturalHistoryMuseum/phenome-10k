const jsonrpc = '2.0';

class RpcError extends Error {
	constructor(message, code){
		super(message);

		this.code = code;
	}
}

function writeResponse(object, response) {
	object.jsonrpc = jsonrpc;
	return response.end(JSON.stringify(object));
}

function wrapError(e) {
	return {
		error: {
			message: e.message,
			code: e.code || -32603
		}
	}
}

async function parseBody(request) {
	let body = '';
	for await(const chunk of request) {
		body += chunk;
	}

	return JSON.parse(body);
}

module.exports = methods => {
	function getMethod(methodName, ctx=methods) {
		const method =	typeof ctx === 'function' ? ctx(methodName) :
			methodName in ctx ? ctx[methodName].bind(ctx) :
			null;
		if(method) {
			return method;
		} else if(methodName.indexOf('.')>=0) {
			const [newCtx, ...parts] = methodName.split('.');
			return Object.hasOwnProperty.call(methods, newCtx) && getMethod(parts.join('.'), methods[newCtx]);
		}
	}

	async function rpcCall(method, params) {
		try {
			const call = getMethod(method);
			if(!call) {
				throw new RpcError(`There is no method called ${method}`, -32601);
			}

			return {
				result: await call(...params)
			}
		} catch(e) {
			return wrapError(e);
		}
	}

	async function getResponse(req){
		try {
			const body = await parseBody(req);
			const { method, params, id } = body;
			responseObject = await rpcCall(method, params);
			responseObject.id = id;
			return responseObject;
		} catch(e) {
			return wrapError(e);
		}
	}

	return async (req,res) => {
		const object = await getResponse(req);
		return writeResponse(object, res);
	}
}
