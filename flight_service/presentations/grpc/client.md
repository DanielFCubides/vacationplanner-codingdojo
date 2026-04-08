# Client GRPC example

## step 1 - generate the gRPC client

```shell
python -m grpc_tools.protoc -I..\..\vacationplanner-codingdojo\flight_scrapper_service\presentations\grpc\ --python_out=. --grpc_python_out=. ..\..\vacationplanner-codingdojo\flight_scrapper_service\presentations\grpc\service.proto
```

## Create a flask app using the clients

```python

from flask import Flask, request, jsonify
import grpc
from presentations.grpc import service_pb2
import service_pb2_grpc

app = Flask(__name__)


@app.route('/greet', methods=['POST'])
def greet():
    name = request.json.get('name', 'World')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(service_pb2.HelloRequest(name=name))
    return jsonify(message=response.message)


if __name__ == '__main__':
    app.run(debug=True)

```