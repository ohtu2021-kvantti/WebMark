FROM python:3.9-alpine3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache gcc musl-dev postgresql-dev

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .