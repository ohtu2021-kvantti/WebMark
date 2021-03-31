FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG LIBMARK_VERSION

RUN apt-get update && apt-get -y install git
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/ohtu2021-kvantti/LibMark@${LIBMARK_VERSION}
COPY . .