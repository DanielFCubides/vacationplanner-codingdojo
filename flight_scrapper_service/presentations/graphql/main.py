from presentations.graphql import schema

try:
    from graphql_server.flask import GraphQLView
except ModuleNotFoundError:
    pass

from flask import Flask


def create_app():
    app = Flask(__name__)

    app.add_url_rule(
        '/graphql_server',
        view_func=GraphQLView.as_view(
            'graphql_server',
            schema=schema.my_schema,
            graphiql=True
        )

    )
    return app


def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
