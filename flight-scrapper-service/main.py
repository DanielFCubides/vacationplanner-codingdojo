from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {"hello":"<p>Hello, World!</p>"}


@app.route("/flights")
def flights():
    #if method == GET
        # retornar lista de vuelos bajo criterios entregados
    return [{"hello":"<p>Hello, World!</p>"},{"hello":"<p>Hello, World!</p>"},{"hello":"<p>Hello, World!</p>"},{"hello":"<p>Hello, World!</p>"}]