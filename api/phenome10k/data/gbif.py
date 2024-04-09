import requests

from phenome10k.models import Taxonomy
from sqlalchemy import and_


def fetch_json(url):
    r = requests.get(url)
    if r.ok:
        return r.json()
    else:
        r.raise_for_status()


def pull_tags(gbif_species_id):
    if not validate_id('species', gbif_species_id):
        return []

    species_url = 'https://api.gbif.org/v1/species/'
    gbif_api_url = species_url + str(gbif_species_id)
    gbif_api_parents = gbif_api_url + '/parents'

    parent_taxa = fetch_json(gbif_api_parents)
    taxon = fetch_json(gbif_api_url)
    tags = []

    def _make_taxonomy_model(json_taxon, is_gbif=True):
        return Taxonomy(
            id=json_taxon['key'],
            name=json_taxon['canonicalName'],
            parent_id=json_taxon.get('parentKey'),
            gbif=is_gbif,
        )

    # sense check rank vs number of parents
    # variety and forma have not been tested; subspecies has
    ranks = ['KINGDOM', 'PHYLUM', 'CLASS', 'ORDER', 'FAMILY', 'GENUS', 'SPECIES']

    if (
        taxon['rank'] == 'SUBSPECIES'
        and len(parent_taxa) < len(ranks)
        and taxon.get('speciesKey')
    ):
        # sometimes the parent for subspecies is genus not species, so add the species manually
        parent_taxa.append(fetch_json(species_url + str(taxon['speciesKey'])))

    try:
        expected_parents = ranks.index(taxon['rank'])
    except ValueError:
        if taxon['rank'] in ['SUBSPECIES', 'VARIETY', 'FORMA']:
            expected_parents = len(ranks)
        else:
            return []
    if len(parent_taxa) == expected_parents:
        tags += [_make_taxonomy_model(t) for t in parent_taxa]
    if expected_parents > len(parent_taxa):
        for r in ranks[:expected_parents]:
            previous_parent = tags[-1].id if len(tags) > 0 else None
            try:
                parent_taxon = next(t for t in parent_taxa if t['rank'] == r)
                parent = _make_taxonomy_model(parent_taxon)
            except StopIteration:
                # try and find an existing child
                parent = Taxonomy.query.filter(
                    and_(Taxonomy.parent_id == previous_parent, Taxonomy.gbif == False)
                ).first()
                if not parent:
                    # create a new item with a very large id
                    current_max = (
                        Taxonomy.query.filter(
                            and_(Taxonomy.id >= 1000000000, Taxonomy.gbif == False)
                        )
                        .order_by(Taxonomy.id.desc())
                        .first()
                    )
                    if current_max:
                        new_id = (
                            current_max.id + 1
                            if previous_parent < current_max.id
                            else previous_parent + 1
                        )
                    else:
                        new_id = 1000000000
                    parent = _make_taxonomy_model(
                        {'key': new_id, 'canonicalName': f'Unknown {r.lower()}'}, False
                    )
            parent.parent_id = previous_parent
            tags.append(parent)

    tags.append(_make_taxonomy_model(taxon))

    return tags


def validate_id(gbif_type, gbif_id):
    if gbif_id is None or gbif_id == '':
        return False
    gbif_api_url = f'https://api.gbif.org/v1/{gbif_type}/{gbif_id}'
    try:
        fetch_json(gbif_api_url)
        return True
    except requests.HTTPError:
        return False
