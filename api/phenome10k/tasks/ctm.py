from ..extensions import scan_store
from .apium import celery


@celery.task()
def create_ctm(scan):
    scan_store.create_ctm(scan)
