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
	function getMethod(methodName) {
		const method = typeof methods === 'function' ? methods(methodName) :
									 methodName in methods ? methods[methodName].bind(methods) :
									 null;

		if(method) {
			return method;
		} else {
			throw new RpcError(`There is no method called ${methodName}`, -32601);
		}
	}

	async function rpcCall(method, params) {
		try {
			const call = getMethod(method);

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
