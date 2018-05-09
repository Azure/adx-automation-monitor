FROM tiangolo/uwsgi-nginx-flask:python:3.6

COPY ./app /app
RUN pip install -r /app/requirements.txt
