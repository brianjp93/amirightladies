# FROM python:3.8-alpine

# RUN apk update && apk upgrade
# RUN apk add --no-cache git \
#     libffi-dev \
#     pkgconfig \
#     gcc \
#     libc-dev \
#     python3-dev \
#     libffi-dev libsodium-dev opus-dev ffmpeg

# RUN mkdir -p /app
# WORKDIR /app

# EXPOSE 8080

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . .

FROM python:3.8-slim-buster

RUN apt-get update; \
    apt-get install -y libffi-dev git \
    libc-dev python3-dev libsodium-dev libopus-dev ffmpeg

RUN mkdir -p /app
WORKDIR /app

EXPOSE 8080

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
