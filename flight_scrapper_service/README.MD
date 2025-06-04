# flight scrapper service

## how to run

Set up the env variable SERVER with the type of server you want to initialized:
- rest
- grpc
- graphql

```shell
export SERVER=rest
```
### Docker compose

Go the the parent folder and intialized the server

```shell
docker compose up flight-scrapper --build
```
Then you can go to localhost:8001/ and check that the project is alive, you should get a message like this one:

```json
{
  "status": "alive",
  "timestamp": "Wed, 04 Jun 2025 01:48:17 GMT"
}
```

### Docker
Then you can create the container 
```shell
docker build . -t flight-scraper
docker run -it -p 5000:5000 flight-scraper
```

