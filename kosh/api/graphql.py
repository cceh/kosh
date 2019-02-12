from kosh.api._api import _api

class graphql(_api):
  pass

# import graphene
# import json
# from collections import namedtuple
# from elasticsearch import Elasticsearch
# from lxml import etree
# from io import StringIO
# from bs4 import BeautifulSoup


# from flask import Flask
# from flask_graphql import GraphQLView
# from dict_schema import DictQuery
# from graphene import Schema
# import os


# # https://stackoverflow.com/questions/50559580/creating-dynamic-schema-on-runtime-graphene?rq=1
# # https://github.com/graphql-python/graphene/issues/336

# class GraEntry(graphene.ObjectType):
#   id = graphene.String()
#   sort_id = graphene.Int()
#   headword_iso = graphene.String()
#   headword_slp1 = graphene.String()
#   headword_hk = graphene.String()
#   headword_deva = graphene.String()
#   headword_gra = graphene.String()
#   headword_ascii = graphene.String()
#   entry_tei_iso = graphene.String()
#   entry_tei_gra = graphene.String()
#   sense_txt_iso = graphene.String()
#   sense_txt_gra = graphene.String()

# class DictEntry(graphene.ObjectType):
#   id = graphene.String()
#   sort_id = graphene.Int()
#   headword_iso = graphene.String()
#   headword_slp1 = graphene.String()
#   headword_hk = graphene.String()
#   headword_deva = graphene.String()
#   headword_ascii = graphene.String()
#   entry_tei_iso = graphene.String()
#   sense_txt_iso = graphene.String()
#   sense_html_iso = graphene.String()

# class DictQuery(graphene.ObjectType):
#   entries = graphene.List(
#     DictEntry,
#     dict_id = graphene.String(),
#     query = graphene.String(),
#     query_type = graphene.String(),
#     field = graphene.String(),
#     size = graphene.Int()
#   )

#   ids = graphene.List(
#     DictEntry,
#     dict_id = graphene.String(),
#     lemma_id = graphene.List(graphene.String),
#     size=graphene.Int()
#   )

#   def resolve_entries(self, info, dict_id, query, query_type, field, size):
#     res = get_from_elastic(dict_id=dict_id, query=query, size=size, query_type=query_type, field=field)
#     parsed_results = select_from_elastic_response(res['hits']['hits'])
#     return json2obj(json.dumps(parsed_results))

#   def resolve_ids(self, info, dict_id, lemma_id, size):
#     res = get_from_elastic(dict_id=dict_id, query=lemma_id, size=size, query_type='ids')
#     parsed_results = select_from_elastic_response(res['hits']['hits'])
#     return json2obj(json.dumps(parsed_results))

# view_func = GraphQLView.as_view('graphql', schema=Schema(query=DictQuery), graphiql=True)

# app = Flask(__name__)
# app.add_url_rule('/dicts/sa/graphql', view_func=view_func)

# if __name__ == '__main__':
#     app.config.update(DEBUG=True)
#     app.run(host='127.0.0.1', port=os.environ.get('PORT', 5001))

# client = Elasticsearch()

# def _json_object_hook(d):
#     return namedtuple('X', d.keys())(*d.values())


# def json2obj(data):
#     print(data)
#     return json.loads(data, object_hook=_json_object_hook)
