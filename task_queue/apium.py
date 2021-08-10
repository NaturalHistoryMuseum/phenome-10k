import os

from celery import Celery

broker_url = os.getenv('BROKER_URL', 'amqp://')
backend_url = os.getenv('BACKEND_URL', 'rpc://')

app = Celery('proj',
             broker=broker_url,
             backend=backend_url,
             include=['task_queue.tasks'])

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
