const path = require('path');

function Rest(objects, baseUrl) {
	return async (req, res) => {
		const resource = path.relative(req.url, baseUrl);

		switch(req.method) {
			case 'POST':
				const id = await objects.create(req, resource);
				res.statusCode = 201;
				res.setHeader('location', path.join(baseUrl, id));
				res.end();
				return true;
			case 'PUT':
				await objects.write(resource, req);
				res.statusCode = 204;
				res.end();
				return true;
			case 'GET':
				const r = await objects.read(resource)
				r.pipe(res);
				return true;
			case 'DELETE':
				await objects.delete(resource);
				res.statusCode = 204;
				res.end();
				return true;
		}
	}
}

module.exports = Rest;
