import urllib.request, json
from app.models import Taxonomy, Scan, db


def fetch_json(url):
  with urllib.request.urlopen(url) as response:
    return json.loads(response.read().decode())

def pull_tags(gbif_id):
  gbif_api_url = "http://api.gbif.org/v1/species/" + str(gbif_id)
  gbif_api_parents = gbif_api_url + "/parents"

  tags = fetch_json(gbif_api_parents) + [fetch_json(gbif_api_url)]

  return [
    Taxonomy(
      id = tag['key'],
      name = tag['vernacularName'] if 'vernacularName' in tag else tag['canonicalName'],
      parent_id = tag['parentKey'] if 'parentKey' in tag else None
    ) for tag in tags
  ]
