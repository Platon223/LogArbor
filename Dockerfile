FROM python:3.11-slim

WORKDIR /app/log_reader

RUN apt-get update && apt-get install -y libssl-dev ca-certificates && \
    echo "[system_default_sect]" >> /etc/ssl/openssl.cnf && \
    echo "MinProtocol = TLSv1" >> /etc/ssl/openssl.cnf && \
    echo "CipherString = DEFAULT@SECLEVEL=1" >> /etc/ssl/openssl.cnf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "4", "-b", "0.0.0.0:8888", "service:app"]