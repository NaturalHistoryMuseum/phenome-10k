const url = require('url');
const http = require('https')

const auth_endpoint = 'https://man-vault-2.nhm.ac.uk:8200/v1/auth';

const options = url.parse(auth_endpoint + '/ldap/login/paulk6');

options.method = "POST"

const options = url.parse(auth_endpoint + '/token/renew');

options.method = "POST"
options.headers = {
  'X-Vault-Token': 's.1zchyxNT2zeL1mIEk2a07cp7'
}

req = http.request(
  options, res => {
    res.setEncoding('utf8')
    let body = '';

    res.on('data', (chunk) => {
      body += chunk;
    });
    res.on('end', () => {
      console.log(body)
  });
  }
)

req.write(JSON.stringify({ 
  //password: 'Bad egg 77.' ,
  ttl: '1h' }));
req.end();