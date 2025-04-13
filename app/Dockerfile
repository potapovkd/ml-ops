FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip & pip install -r /app/requirements.txt