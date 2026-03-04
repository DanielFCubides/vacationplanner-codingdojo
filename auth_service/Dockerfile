FROM python:3.13-slim AS base

ARG VIRTUAL_ENV=/opt/app/env

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /auth_service

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS dev

WORKDIR /auth_service

COPY --from=base /opt/app/env /opt/app/env
ENV PATH="/opt/app/env/bin:$PATH" \
    PYTHONPATH="/auth_service"

COPY requirements_dev.txt .
RUN pip install --no-cache-dir -r requirements_dev.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "dev", "presentation/main.py", "--host", "0.0.0.0", "--port", "8000"]