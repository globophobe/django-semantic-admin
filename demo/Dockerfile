FROM python:3.9-slim-buster

ARG POETRY_EXPORT
ARG SECRET_KEY
ARG SENTRY_DSN

ENV SECRET_KEY $SECRET_KEY
ENV SENTRY_DSN $SENTRY_DSN

ADD demo /demo/demo
ADD demo_app /demo/demo_app
ADD static /demo/static
ADD media /demo/media
ADD templates /demo/templates
ADD db.sqlite3 /demo/db.sqlite3

RUN pip install --no-cache-dir $POETRY_EXPORT "django<4" django-semantic-admin sentry-sdk

# Start the server
ENTRYPOINT ["gunicorn", "--chdir", "/demo", "--bind", "0.0.0.0:8080", "demo.wsgi:application"]
