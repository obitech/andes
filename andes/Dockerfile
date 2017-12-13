FROM python:3.6-slim

EXPOSE 5000 5001

COPY system/api/code /andes/api/code
COPY system/api/requirements_container.txt /andes/api
COPY system/templates /andes/templates
COPY system/api/*.ini /andes/api

WORKDIR /api

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install build-essential -y \
    && pip3 install -r requirements_.txt \
    && apt-get clean

CMD ["uwsgi","uwsgi.ini"]