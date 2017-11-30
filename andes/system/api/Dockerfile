FROM python:3.6-slim

EXPOSE 5000 5001

COPY code/ /api/code
COPY *.txt /api
COPY *.ini /api

WORKDIR /api

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install build-essential -y \
    && pip3 install -r requirements.txt \
    && apt-get clean

CMD ["uwsgi","uwsgi.ini"]