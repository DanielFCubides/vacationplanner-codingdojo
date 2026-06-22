FROM python:3.10-slim-buster AS builder

ENV VIRTUAL_ENV=/opt/app/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


FROM builder AS primary

WORKDIR /vacation_stay_scrapper

COPY --from=builder /opt/app/env /opt/app/env
ENV PATH="/opt/app/env/bin:$PATH" \
    PYTHONPATH="/vacation_stay_scrapper"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM builder AS tests

COPY --from=builder /opt/app/env /opt/app/env
ENV PATH="/opt/app/env/bin:$PATH"

COPY requirements_test.txt /tmp/requirements_test.txt
RUN pip install --no-cache-dir -r /tmp/requirements_test.txt

WORKDIR /vacation_stay_scrapper
COPY . .

CMD ["pytest", ".", "--cov", ".", "--cov-report", "html"]
