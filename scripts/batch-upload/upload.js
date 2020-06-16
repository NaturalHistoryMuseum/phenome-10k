const fs = require('fs');
const Client = require('./client');
const { css, xpath } = require('./selectors');
const { waitFor } = require('./utils');

/**
 * Upload multiple files to phenome10k
 *
 * Requires records.json to contain array of objects like this:
 *   {
    "scientific name": "Salamandra salamandra gigliolii",
    "alt name (optional)": "",
    "source filename": "Salamandra_salamandra_gigliolii_BMNH_1852.12.11.64",
    "specimen id (optional)": "BMNH_1852.12.11.64",
    "specimen location (optional)": "Natural History Museum, UK",
    "specimen url (optional)": "",
    "description": "",
    "geologic age": "extant",
    "ontogenetic age": "adult",
    "elements": "cranium",
    "gbif backbone id (if known)": ""
  }

 * Requires source files to be in the files directory named [source filename].stl.zip
 * To zip each file, run .zip {$directory}
 */

const sleep = ms => new Promise(r => setTimeout(r, ms));

const config = {
  path: '/',
  capabilities: {
    browserName: 'firefox',
    timeouts: {
      implicit: 5000
    }
  },
  logLevel: 'debug'
}

const readIx = (() => {
  try {
    return require('./ix.json')
  } catch(e) {
    return 0;
  }
});

const saveIx = ix => fs.writeFileSync('./ix.json', String(ix));

const delIx = () => fs.unlinkSync('./ix.json');

const ucfirst = s=>s.replace(/./, a=>a.toUpperCase());

Client.run(config, async (window) => {
  await window.maximizeWindow();
  await window.navigateTo('https://phenome10k.org/login');

  const adminUser = 'admin';
  const adminPassword = process.env.ADMIN /* get this from vault */;

  await window.find(css('input[name=email]')).sendKeys(adminUser);
  await window.find(css('input[name=password]')).sendKeys(adminPassword);
  await window.find(css('#submit')).click().waitUntilStale();

  const records = require('./records.json');

  console.log('loop for');
  for(let ix = readIx(); ix < records.length; saveIx(++ix)) {
    await window.navigateTo('https://phenome10k.org/scans/create/');
    const record = records[ix];
    const fileInput = await window.find(css('input[name=file]'));
    const filename = './files/' + record['source filename'] + '.stl.zip';
    console.log(filename);
    const zip = require.resolve(filename)

    await fileInput.sendKeys(zip);

    await window.find(css('.Upload__still-capture-name input')).sendKeys('Preview');

    await waitFor(() => window.find(css('.CtmViewer')), 10 * 60 * 1000);

    // Wait for CTM to actually render
    await sleep(10000);

    await window.find(css('.Upload__still-capture-name button')).click();
    await window.find(css('.Upload__still-image'));

    await window.find(css('input[name=scientific_name]')).sendKeys(record['scientific name']);

    // Make sure any Vue rendering doesn't mess things up
    await sleep(1000);

    await window.find(css('input[name=specimen_id]')).sendKeys(record["specimen id (optional)"]);
    await window.find(css('input[name=specimen_location]')).sendKeys(record["specimen location (optional)"]);
    await window.find(css('input[name=specimen_url]')).sendKeys(record["specimen url (optional)"]);
    await window.find(css('textarea[name=description]')).sendKeys(record["description"]);

    await window.find(xpath(`//input[@name='geologic_age']/following-sibling::label[text() = '${ucfirst(record['geologic age'])}']`)).click();
    await window.find(xpath(`//input[@name='ontogenic_age']/following-sibling::label[text() = '${ucfirst(record['ontogenetic age'])}']`)).click();
    await window.find(xpath(`//input[@name='elements']/following-sibling::label[text() = '${ucfirst(record['elements'])}']`)).click();
    await window.find(xpath(`//input[@name='published']/following-sibling::label`)).click();

    try {
      await window.find(css('.Upload__submit button')).click().waitUntilStale();
    } catch(e){
      await sleep(15000);
      throw e;
    }
  }

  await sleep(15000);

  console.log('Finished');
  delIx();
});
