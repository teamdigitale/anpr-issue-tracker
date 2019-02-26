FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8

COPY ./app /app

RUN pip3 install -r /app/app/requirements.txt
CMD ["/usr/bin/supervisord"]
