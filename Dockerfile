FROM tiangolo/uwsgi-nginx-flask:python3.6

ARG VERSION

COPY ./app /app
COPY ./Pipfile.lock /app/Pipfile.lock

RUN pip install -U pip pipenv && \
    pipenv install --ignore-pipfile && \
    pipenv install --ignore-pipfile --system && \
    pipenv --rm && \
    echo $VERSION > /app/app_version

ENV STATIC_PATH /app/app/static