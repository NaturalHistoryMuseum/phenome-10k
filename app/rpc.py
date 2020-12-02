import requests
import json

def rpc(url, method, params):
	payload = {
			"method": method,
			"params": params,
			"jsonrpc": "2.0",
			"id": 0,
	}
	response = requests.post(url, json=payload).json()
	if("error" in response):
		raise Exception(response["error"]["message"])
	return response["result"]
