FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . $WORKDIR

CMD [ "python3", "-m" , "flask", "--app", "main",  "run",  "--host=0.0.0.0"]