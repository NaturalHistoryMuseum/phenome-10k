FROM python:3.8

RUN apt-get update && apt-get install -y --no-install-recommends \
                mariadb-client

COPY ./requirements.txt /var/phenome10k/www/requirements.txt
COPY ./docker/app-flask/entrypoint /deploy/entrypoint
COPY ./app /var/phenome10k/www/app
COPY ./migrations /var/phenome10k/www/migrations
COPY ./config.py /var/phenome10k/www/config.py

WORKDIR /var/phenome10k/www

RUN pip install -r requirements.txt

# just running flask db upgrade doesn't work - it has to be run in the entrypoint for some reason
ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["flask", "run", "--host", "0.0.0.0"]
