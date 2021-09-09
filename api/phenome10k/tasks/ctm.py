from .apium import celery
from ..extensions import scan_store


@celery.task()
def create_ctm(scan):
    scan_store.create_ctm(scan)
