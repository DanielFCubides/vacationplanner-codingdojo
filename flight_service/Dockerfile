FROM python:3.11.15-bookworm as builder

ENV VIRTUAL_ENV=/opt/app/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


FROM builder as dev

WORKDIR /flight_service
COPY . $WORKDIR

COPY --from=builder /opt/app/env /opt/app/env
ENV PATH=/opt/app/env:$PATH

CMD ["python3", "main.py"]


FROM dev as tests

COPY requirements_test.txt /tmp/requirements_test.txt
RUN pip install --no-cache-dir -r /tmp/requirements_test.txt

CMD ["pytest", ".", "--cov", ".", "--cov-report", "html"]

FROM python:3.11.15-bookworm as prod

ENV VIRTUAL_ENV=/opt/app/env
COPY --from=builder /opt/app/env /opt/app/env
ENV PATH=/opt/app/env/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /flight_service
COPY . .

RUN useradd --create-home --uid 10001 app && chown -R app:app /flight_service
USER app

EXPOSE 8080
CMD ["python", "production.py"]
