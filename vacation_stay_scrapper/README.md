# Vacation / Stay Scrapper


## How to run

Directly

```shell
 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```


```shell
docker build . -t vacation_planner
docker run --rm -p 80:80 -t vacation_planner
```

using docker compose

```shell
docker compose build
docker compose up -d vacation-planner
```

## Run the test suit
navigate until project's folder and run the command locally

```shell
cd vacation_stay_scrapper
pytest .
```

or run with docker
```shell
docker compose up -d vacation-planner #(if its not up already)
docker compose exec vacation-planner pytest .
```