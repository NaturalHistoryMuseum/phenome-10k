FROM python:3.8

RUN apt-get update -y && apt-get install mariadb-client -y

COPY ./docker/app-flask/entrypoint /deploy/entrypoint
COPY ./api /var/phenome-10k/www/api

WORKDIR /var/phenome-10k/www/api

RUN python setup.py develop

# run any initialisation or pre-run checks
ENTRYPOINT ["/bin/bash", "/deploy/entrypoint"]

CMD ["flask", "run", "--host", "0.0.0.0"]
