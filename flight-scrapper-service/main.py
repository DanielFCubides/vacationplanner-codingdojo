from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"hello": "<p>Hello, World!</p>"}


@app.route("/flights", methods=['GET'])
def flights():
    return [{"hello": "<p>Hello, World!</p>"}, {"hello": "<p>Hello, World!</p>"}, {"hello": "<p>Hello, World!</p>"},
                {"hello": "<p>Hello, World!</p>"}], 200
