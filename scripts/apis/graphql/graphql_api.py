from flask import Flask
from flask_graphql import GraphQLView
from dict_schema import DictQuery
from graphene import Schema
import os

view_func = GraphQLView.as_view(
    'graphql', schema=Schema(query=DictQuery), graphiql=True)

app = Flask(__name__)
app.add_url_rule('/dicts/sa/graphql', view_func=view_func)

if __name__ == '__main__':
    app.config.update(
        DEBUG=True)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5001))
