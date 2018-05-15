FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./app /app
ENV STATIC_PATH /app/app/static
RUN pip install -r /app/requirements.txt
