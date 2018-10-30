from flask import Flask
from flask_graphql import GraphQLView
from schema_vei import VEIQuery
from graphene import Schema
import os

view_func = GraphQLView.as_view(
    'graphql', schema=Schema(query=VEIQuery), graphiql=True)

app = Flask(__name__)
app.add_url_rule('/dicts/vei/graphql', view_func=view_func)

if __name__ == '__main__':
    app.config.update(
        DEBUG=True)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5007))
