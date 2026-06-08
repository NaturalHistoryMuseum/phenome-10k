#!/usr/bin/env python3

import getpass
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

user = input('Vault LDAP username: ')
pswd = getpass.getpass('Vault LDAP password: ')
vault_url = os.environ.get('VAULT_ADDR')
if not vault_url:
    vault_url = input('Vault URL: ')
vault_login_url = f'{vault_url}/v1/auth/ldap/login/{user}'
post_fields = {'password': pswd}
headers = {
    'User-Agent': 'phenome10k deployment script',
    'Content-Type': 'application/json',
}

request = Request(
    vault_login_url, data=json.dumps(post_fields).encode(), headers=headers
)
try:
    resp = urlopen(request)
    content = resp.read().decode()
    auth = json.loads(content)['auth']
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
    print(f"Got token OK. It's valid for {duration:g} {unit}.")
    print(token)
except HTTPError as e:
    print(f'Failed to get a token, sorry. Vault says:', file=sys.stderr)
    resp = e.read().decode()
    errors = json.loads(resp)['errors']
    sys.exit('\n'.join(errors))
except URLError as e:
    print(
        f'Could not connect to vault server. Are you on the museum network?',
        file=sys.stderr,
    )
    sys.exit(e)
