FROM python:3.7-alpine3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache gcc musl-dev postgresql-dev git

RUN git clone https://github.com/ohtu2021-kvantti/LibMark
WORKDIR /LibMark
RUN pip install -e .
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .