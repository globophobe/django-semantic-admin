FROM python:3.7-slim-buster

ARG POETRY_EXPORT
ARG SECRET_KEY

ENV SECRET_KEY $SECRET_KEY

ADD demo /demo/demo
ADD demo_app /demo/demo_app
ADD static /demo/static
ADD media /demo/media
ADD db.sqlite3 /demo/sqlite3

RUN pip install --no-cache-dir $POETRY_EXPORT django-semantic-admin

# Start the server
ENTRYPOINT ["gunicorn", "--chdir", "/demo", "demo.wsgi:application"]
