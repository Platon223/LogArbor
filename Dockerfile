FROM python:3.14-slim

WORKDIR /app/log_reader

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:8888", "service:app"]