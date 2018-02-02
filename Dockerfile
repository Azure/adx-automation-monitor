FROM python:3.6-jessie

COPY ./app /app
RUN pip install -r /app/requirements.txt

CMD python /app/monitor.py
