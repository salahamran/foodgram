FROM python:3.10

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram_backend.wsgi"]
