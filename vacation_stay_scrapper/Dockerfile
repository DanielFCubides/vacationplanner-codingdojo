FROM python:3.10-slim-buster as test

WORKDIR /test
COPY . /test
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN echo "Running test.."
RUN pytest

FROM test
RUN echo "Building image..."
WORKDIR /app
COPY . $WORKDIR

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

