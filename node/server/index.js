const Admin = require('./admin-api');
const Objects = require('./object-storage');
const Scans = require('./scans');
const Web = require('./www');

function app(renderer, fileDirectory, db) {
	const objects = Objects(fileDirectory);
	const scans = Scans(db);
	const admin = Admin(renderer, objects, scans);
	const web = Web(objects, scans);
	return {
		admin,
		web
	}
}

module.exports = app;
