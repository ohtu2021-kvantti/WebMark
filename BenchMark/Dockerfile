FROM condaforge/mambaforge:4.10.1-0

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG LIBMARK_VERSION

WORKDIR /code

COPY environment.yml .
RUN mamba env create -f environment.yml
# use the conda environment for the subsequent commands
SHELL ["conda", "run", "-n", "benchmark", "/bin/sh", "-c"]

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/ohtu2021-kvantti/LibMark.git@${LIBMARK_VERSION}
COPY . .