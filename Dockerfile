FROM python:3.12-alpine

ARG WHEEL
ARG UV_EXPORT
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
RUN pip install --no-cache-dir $UV_EXPORT
RUN rm $WHEEL

ENTRYPOINT ["gunicorn", "--chdir", "/demo", "--bind", "0.0.0.0:8080", "--threads", "2", "--timeout", "0", "--preload", "demo.wsgi:application"]
