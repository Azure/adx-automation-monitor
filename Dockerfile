FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./app /app
COPY ./Pipfile.lock /app/Pipfile.lock

ENV STATIC_PATH /app/app/static
RUN pip install -U pip pipenv && \
    pipenv install --ignore-pipfile && \
    pipenv install --ignore-pipfile --system && \
    pipenv --rm
