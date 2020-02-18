#!/usr/bin/env python3

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import sys
import getpass

sys.stderr.write('Vault LDAP username: ')
user = input()
pswd = getpass.getpass('Vault LDAP password: ')

vault_url = 'https://man-vault-2.nhm.ac.uk:8200/v1/auth/ldap/login/' + user # Set destination URL here
post_fields = {'password': pswd}     # Set POST fields here

request = Request(vault_url, json.dumps(post_fields).encode())
try:
  resp = urlopen(request).read().decode()
  auth = json.loads(resp)['auth']
  token = auth['client_token']
  duration = auth['lease_duration']
  unit = 'seconds'
  if duration >= 60:
  	duration = duration / 60
  	unit = 'minutes'

  	if duration >= 60:
  		duration = duration / 60
  		unit = 'hours'

  		if duration >= 24:
  			duration = duration / 24
  			unit = 'days'
  print(f'Got token OK. It\'s valid for {duration:g} {unit}.', file=sys.stderr)
  print(token)
except HTTPError as e:
  print(f'Failed to get a token, sorry. Vault says:', file=sys.stderr)
  resp = e.read().decode()
  errors = json.loads(resp)['errors']
  sys.exit('\n'.join(errors))
except URLError as e:
  print(f'Could not connect to vault server. Are you on the museum network?', file=sys.stderr)
  sys.exit(e)
