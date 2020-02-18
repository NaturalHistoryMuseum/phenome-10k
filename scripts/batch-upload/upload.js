const fs = require('fs');
const Client = require('./client');
const { css, xpath } = require('./selectors');
const { waitFor } = require('./utils');


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
    return String(fs.readFileSync('./ix')).trim()
  } catch(e) {
    return 0;
  }
});

const saveIx = ix => fs.writeFileSync('./ix', String(ix));

const ucfirst = s=>s.replace(/./, a=>a.toUpperCase());

Client.run(config, async (window) => {
  await window.navigateTo('https://phenome10k.org/login');

  const adminUser = 'admin';
  const adminPassword = /* get this from vault */;

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

    await new Promise(r => setTimeout(r, 10000));

    await window.find(css('.Upload__still-capture-name button')).click();
    await window.find(css('.Upload__still-image'));

    await window.find(css('input[name=scientific_name]')).sendKeys(record['scientific name']);
    await window.find(css('input[name=specimen_id]')).sendKeys(record["specimen id (optional)"]);
    await window.find(css('input[name=specimen_location]')).sendKeys(record["specimen location (optional)"]);

    await window.find(xpath(`//input[@name='geologic_age']/following-sibling::label[text() = '${ucfirst(record['geologic age'])}']`)).click();
    await window.find(xpath(`//input[@name='ontogenic_age']/following-sibling::label[text() = '${ucfirst(record['ontogenetic age'])}']`)).click();
    await window.find(xpath(`//input[@name='elements']/following-sibling::label[text() = '${ucfirst(record['elements'])}']`)).click();
    await window.find(xpath(`//input[@name='published']/following-sibling::label`)).click();
    
    await window.find(css('.Upload__submit button')).click().waitUntilStale();
  }

  await new Promise(r => setTimeout(r, 15000));
});
