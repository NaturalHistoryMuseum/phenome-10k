import requests

from phenome10k.models import Taxonomy


def fetch_json(url):
    r = requests.get(url)
    if r.ok:
        return r.json()
    else:
        r.raise_for_status()


def pull_tags(gbif_species_id):
    if not validate_id('species', gbif_species_id):
        return []

    gbif_api_url = 'https://api.gbif.org/v1/species/' + str(gbif_species_id)
    gbif_api_parents = gbif_api_url + '/parents'

    tags = fetch_json(gbif_api_parents) + [fetch_json(gbif_api_url)]

    return [
        Taxonomy(
            id=tag['key'],
            name=tag.get('vernacularName', tag['canonicalName']),
            parent_id=tag.get('parentKey'),
        )
        for tag in tags
    ]


def validate_id(gbif_type, gbif_id):
    if gbif_id is None or gbif_id == '':
        return False
    gbif_api_url = f'https://api.gbif.org/v1/{gbif_type}/{gbif_id}'
    try:
        fetch_json(gbif_api_url)
        return True
    except requests.HTTPError:
        return False
