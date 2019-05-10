from app import app, db
from app.models import Taxonomy, Scan
from app.gbif import pull_tags

def update_tags():
  """ Updates taxonomy tags from gbif backbone and deletes unused ones """
  for scan in Scan.query.filter(Scan.gbif_id).all():
    tags = [
      db.session.merge(tag) for tag in pull_tags(scan.gbif_id)
    ]
    scan.taxonomy = tags

  for tax in Taxonomy.query.filter(db.not_(Taxonomy.scans.any())):
    db.session.delete(tax)
  db.session.commit()

update_tags()
