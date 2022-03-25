FROM python:3.8-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache git \
    libffi-dev \
    pkgconfig \
    gcc \
    libc-dev \
    python3-dev

RUN mkdir -p /app
WORKDIR /app

EXPOSE 8080

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
