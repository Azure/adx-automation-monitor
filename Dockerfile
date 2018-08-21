FROM tiangolo/uwsgi-nginx-flask:python3.6

# The build parameter indicates the unique app version. It is usually the git commit hash
ARG VERSION

# The build parameter of the URI to the source code repository. It is used to generate URI to the source commit
ARG SOURCE_REPO

COPY ./app /app
COPY ./Pipfile.lock /app/Pipfile.lock

RUN pip install -U pip pipenv && \
    pipenv install --ignore-pipfile && \
    pipenv install --ignore-pipfile --system && \
    pipenv --rm && \
    echo $VERSION > /app/app_version && \
    echo $SOURCE_REPO > /app/source_repo

ENV STATIC_PATH /app/app/static