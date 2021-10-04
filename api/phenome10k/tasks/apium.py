from celery import Celery

celery = Celery('phenome10k', autofinalize=False)
