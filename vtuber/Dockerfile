FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    && pip install --no-cache-dir --user -r ./requirements.txt  \
    && apt-get install -y ffmpeg

COPY . ./

CMD ["python", "vtuber_server.py"]