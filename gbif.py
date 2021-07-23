from app import db
from app.gbif import pull_tags
from app.models import Taxonomy, Scan


def update_tags():
    """ Updates taxonomy tags from gbif backbone and deletes unused ones """
    print('Updating tags:')
    for scan in Scan.query.filter(Scan.gbif_id).all():
        tags = [
            db.session.merge(tag) for tag in pull_tags(scan.gbif_id)
        ]
        scan.taxonomy = tags
        print(' - ', scan.scientific_name)

    print('Deleting tags:')
    for tax in Taxonomy.query.filter(db.not_(Taxonomy.scans.any())):
        print(' - ', tax.name)
        db.session.delete(tax)
    db.session.commit()


update_tags()
