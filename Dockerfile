FROM python:3.13-alpine

RUN apk add --no-cache curl bash build-base

ENV PYTHONUNBUFFERED=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR ./quizapp

COPY pyproject.toml poetry.lock* README.md ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .

RUN chmod +x /quizapp/start.sh

VOLUME ["/data"]

EXPOSE 8000
