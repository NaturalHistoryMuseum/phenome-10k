FROM python:3.8

RUN apt-get update -y


COPY ./docker/app-celery/requirements.txt /deploy/requirements.txt
RUN pip install -r /deploy/requirements.txt

WORKDIR /var/phenome-10k/www
RUN pip list

CMD ["celery", "--app", "task_queue.apium:app", "worker", "-l", "INFO"]
