FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip & pip install -r /app/requirements.txt

CMD ["python", "main.py"]
