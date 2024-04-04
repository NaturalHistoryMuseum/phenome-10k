const fs = require('fs');

const readIx = () => {
  try {
    return require('./ix.json');
  } catch (e) {
    return 0;
  }
};

const ix = readIx();

const file = './records.json';

const records = require(file);

const r = records[ix];
records.splice(ix, 1);
records.push(r);

fs.writeFileSync(file, JSON.stringify(records, null, 2));

console.log('Moved record ', ix);
