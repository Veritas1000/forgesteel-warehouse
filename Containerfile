FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

COPY forgesteel_warehouse/ forgesteel_warehouse/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "forgesteel_warehouse:init_app()"]