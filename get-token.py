import urllib.request
import urllib.parse

auth_endpoint = 'https://man-vault-2.nhm.ac.uk:8200/v1/auth'
#curl --request POST --data '{"password": "Bad egg 77."}' 
#url = '/ldap/login/paulk6'
# req =  request.Request(<your url>, data=data) # this will make the method "POST"
# resp = request.urlopen(req)
#print(f.read().decode('utf-8'))

req =  urllib.request.Request(auth_endpoint + '/token/create-orphan', data={ 'ttl': '1h' }) # this will make the method "POST"
req.add_header('X-Vault-Token', 's.1zchyxNT2zeL1mIEk2a07cp7')
resp = request.urlopen(req)
print(resp.read().decode('utf-8'))