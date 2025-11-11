FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

COPY forgesteel_warehouse/ forgesteel_warehouse/

COPY container/ .
RUN chmod +x runWarehouse.sh

VOLUME /data

ENV DATABASE_URI=sqlite:////data/db.sqlite
ENV FSW_CONFIG_PATH=/data/config.json

EXPOSE 5000

CMD ["./runWarehouse.sh"]