FROM python:3.10

COPY ./api/requirements.txt /deploy/requirements.txt
RUN pip install -r /deploy/requirements.txt

WORKDIR /var/phenome-10k/www/api

CMD celery --app phenome10k.celery_worker flower --broker_api=$BROKER_API -l INFO
