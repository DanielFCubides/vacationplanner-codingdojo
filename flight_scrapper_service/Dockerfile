FROM python:3.10-slim-buster as test

WORKDIR /test
COPY . /test
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pytest

FROM test
RUN echo "Building image..."
WORKDIR /app
COPY . $WORKDIR

CMD [ "python3", "-m" , "flask", "--app", "main",  "run",  "--host=0.0.0.0"]