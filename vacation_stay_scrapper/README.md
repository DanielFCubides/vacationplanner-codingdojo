# Vacation / Stay Scrapper


## How to run

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