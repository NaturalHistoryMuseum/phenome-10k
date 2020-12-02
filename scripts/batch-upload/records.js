#!/usr/bin/env node
const csv = require('csvtojson');
const fs = require('fs');

csv().fromFile(process.argv[2]).then(
	records => fs.writeFileSync('records.json', JSON.stringify(records, null, 2))
)
