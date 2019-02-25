FROM tiangolo/uwsgi-nginx:python3.6-alpine3.8

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD python3 run.py
