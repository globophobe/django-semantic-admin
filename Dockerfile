FROM python:3.10-alpine

ARG WHEEL
ARG POETRY_EXPORT
ARG SECRET_KEY
ARG SENTRY_DSN

ENV SECRET_KEY $SECRET_KEY
ENV SENTRY_DSN $SENTRY_DSN

COPY dist/$WHEEL /
COPY demo/demo /demo/demo
COPY demo/demo_app /demo/demo_app
COPY demo/static /demo/static
COPY demo/media /demo/media
COPY demo/templates /demo/templates
COPY demo/db.sqlite3 /demo/db.sqlite3

RUN pip install --no-cache-dir wheel
RUN pip install $WHEEL
RUN pip install --no-cache-dir $POETRY_EXPORT sentry-sdk
RUN rm $WHEEL

# Start the server
ENTRYPOINT ["gunicorn", "--chdir", "/demo", "--bind", "0.0.0.0:8080", "demo.wsgi:application"]
