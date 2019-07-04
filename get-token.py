from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import sys
import getpass

user = input('LDAP username: ')
pswd = getpass.getpass('Password:')

vault_url = 'https://man-vault-2.nhm.ac.uk:8200/v1/auth/ldap/login/' + user # Set destination URL here
post_fields = {'password': pswd}     # Set POST fields here

request = Request(vault_url, json.dumps(post_fields).encode())
try:
  resp = urlopen(request).read().decode()
  auth = json.loads(resp)['auth']
  token = auth['client_token']
  duration = auth['lease_duration']
  unit = 's'
  if duration >= 60:
  	duration = duration / 60
  	unit = 'm'

  	if duration >= 60:
  		duration = duration / 60
  		unit = 'h'

  		if duration >= 24:
  			duration = duration / 24
  			unit = 'd'
  print(f'Token valid for {duration}{unit}', file=sys.stderr)
  prin(token)
except HTTPError as e:
  resp = e.read().decode()
  errors = json.loads(resp)['errors']
  sys.exit('\n'.join(errors))