FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

COPY . /app/
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "worder.wsgi:application"]