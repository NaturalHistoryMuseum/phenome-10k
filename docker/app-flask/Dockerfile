FROM python:3.8

RUN apt-get update -y && apt-get install mariadb-client -y

COPY ./docker/app-flask/entrypoint /deploy/entrypoint
COPY ./requirements.txt /var/phenome-10k/www/requirements.txt
COPY ./app /var/phenome-10k/www/app
COPY ./migrations /var/phenome-10k/www/migrations
COPY ./config.py /var/phenome-10k/www/config.py

WORKDIR /var/phenome-10k/www

RUN pip install -r requirements.txt

# run any initialisation or pre-run checks
ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["flask", "run", "--host", "0.0.0.0"]
