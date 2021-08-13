FROM python:3.8

COPY ./requirements.txt /var/phenome10k/www/requirements.txt
COPY ./docker/app-flask/entrypoint /deploy/entrypoint
COPY ./app /var/phenome10k/www/app
COPY ./migrations /var/phenome10k/www/migrations
COPY ./config.py /var/phenome10k/www/config.py

WORKDIR /var/phenome10k/www

RUN pip install -r requirements.txt

# run any initialisation or pre-run checks
ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["flask", "run", "--host", "0.0.0.0"]
