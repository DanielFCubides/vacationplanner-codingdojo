FROM python:3.10-slim-buster as builder

ENV VIRTUAL_ENV=/opt/app/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


FROM builder as primary

WORKDIR /flight_scrapper_service
COPY . $WORKDIR

COPY --from=builder /opt/app/env /opt/app/env
ENV PATH=/opt/app/env:$PATH

EXPOSE 8001

CMD [ "python3", "main.py"]


FROM builder as tests

COPY requirements_test.txt /tmp/requirements_test.txt

COPY --from=builder /opt/app/env /opt/app/env
ENV PATH=/opt/app/env:$PATH

RUN pip install --no-cache-dir -r /tmp/requirements_test.txt

WORKDIR /vacation_stay_scrapper
COPY . $WORKDIR

CMD ["pytest", ".", "--cov", ".", "--cov-report", "html"]