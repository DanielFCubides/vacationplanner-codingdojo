from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"hello": "<p>Hello, World!</p>"}


@app.route("/flights", methods=['GET'])
def flights():
    if request.method == 'GET':
        return [{"hello": "<p>Hello, World!</p>"}, {"hello": "<p>Hello, World!</p>"}, {"hello": "<p>Hello, World!</p>"},
                {"hello": "<p>Hello, World!</p>"}]
    return "empty", 404
