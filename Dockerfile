FROM python:3.11-slim

WORKDIR /app/log_reader

RUN apt-get update && apt-get install -y libssl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "4", "-b", "0.0.0.0:8888", "service:app"]