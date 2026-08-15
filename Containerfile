FROM python:3.13-slim-trixie AS builder

LABEL org.opencontainers.image.title="Forge Steel Warehouse"
LABEL org.opencontainers.image.description="A data backend for Forge Steel"

WORKDIR /app

COPY pyproject.toml requirements.txt ./

RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip && \
    pip install --root-user-action=ignore --no-cache-dir -r requirements.txt --target /packages

COPY src/ ./

RUN ls && pip install --root-user-action=ignore --no-cache-dir . --target /packages

FROM gcr.io/distroless/python3-debian13

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /packages /packages
COPY container/ ./
COPY migrations/ migrations/

ENV PYTHONPATH="/packages:/app"

VOLUME /data

ENV DATABASE_URI=sqlite:////data/db.sqlite
ENV FSW_CONFIG_PATH=/data/config.json

EXPOSE 5000

CMD ["standalone.py"]
