FROM python:3.8.15-slim

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python", "file_server.py"]