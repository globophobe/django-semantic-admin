FROM python:3.12-alpine

ARG WHEEL
ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY dist/$WHEEL /
COPY dist/deploy-requirements.txt /requirements.txt
COPY demo/demo /demo/demo
COPY demo/demo_app /demo/demo_app
COPY demo/static /demo/static
COPY demo/media /demo/media
COPY demo/templates /demo/templates
COPY demo/db.sqlite3 /demo/db.sqlite3

RUN pip install --no-cache-dir wheel
RUN pip install $WHEEL
RUN pip install --no-cache-dir -r /requirements.txt
RUN rm $WHEEL

ENTRYPOINT ["gunicorn", "--chdir", "/demo", "--bind", "0.0.0.0:8080", "--threads", "2", "--timeout", "0", "--preload", "demo.wsgi:application"]
