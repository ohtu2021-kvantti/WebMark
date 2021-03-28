FROM continuumio/miniconda3:4.9.2-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY environment.yml .
RUN conda env create -f environment.yml
# use the conda environment for the subsequent commands
SHELL ["conda", "run", "-n", "benchmark", "/bin/sh", "-c"]

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/ohtu2021-kvantti/LibMark.git
COPY . .