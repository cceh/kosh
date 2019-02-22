from flask import Flask, Response, request
from kosh.api._api import _api
from kosh.utils import concretemethod, logger


class restful(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, flsk: Flask) -> None:
    '''
    todo: docs
    '''
    path = lambda p: '{}/{}'.format(self.path, p)
    logger().info('Deploying RESTful endpoint %s', self.path)

    flsk.add_url_rule(self.path, self.path, self.info)
    flsk.add_url_rule(path('ids'), path('ids'), self.ids)
    flsk.add_url_rule(path('entries'), path('entries'), self.entries)

  def info(self) -> Response:
    '''
    todo: docs
    '''
    return self.respond_json({
      'dict': self.elex.uid,
      'fields': self.emap
    })

  def ids(self):
    ids = request.args.getlist('ids')

    print(ids)

    return self.respond_json({ })

  def entries(self):
    field = request.args.get('field')
    query = request.args.get('query')
    query_type = request.args.get('query_type')
    size = request.args.get('size')

    print(field, query, query_type, size)

    return self.respond_json({ })


# import json
# import os
# import re
# import sys
# import urllib.parse
# import configparser
# import flask
# from elasticsearch import Elasticsearch
# from flask import make_response
# from indic_transliteration.xsanscript import SchemeMap, SCHEMES, HK, SLP1, DEVANAGARI
# from werkzeug.routing import Map, Rule
# from werkzeug.wsgi import DispatcherMiddleware

# client = Elasticsearch()
# conf_parser = configparser.ConfigParser()
# conf_path = r'../../../utils/rest.conf'
# conf_parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), conf_path))

# app = flask.Flask(__name__)
# app.config["APPLICATION_ROOT"] = conf_parser.get('APP_INFO', 'APPLICATION_ROOT')
# app.config["APPLICATION_NAME"] = conf_parser.get('APP_INFO', 'APPLICATION_NAME')

# MAX_RESULTS = 100
# re_integer_arg = re.compile(r'^[0-9]+$')

# scheme_slp1_deva = SchemeMap(SCHEMES[SLP1], SCHEMES[DEVANAGARI])
# scheme_slp1_hk = SchemeMap(SCHEMES[SLP1], SCHEMES[HK])


# def clip(i, min_, max_):
#     return max(min(int(i), max_), min_)


# def arg(name, default, regex, msg=None):
#     arg = flask.request.args.get(name, default)
#     if not regex.match(arg):
#         if msg is None:
#             msg = 'Invalid %s parameter' % name
#         flask.abort(msg)
#     return arg


# ####


# def make_json_response(obj):
#     resp = flask.Response(json.dumps(obj, indent=2, ensure_ascii=False), mimetype='application/json')
#     resp.headers['Access-Control-Allow-Origin'] = '*'
#     resp.headers["Content-Type"] = "application/json; charset=utf-8"
#     return resp


# ### here we go

# @app.endpoint('info')
# def info():
#     """ Endpoint.  The root of the application. """

#     info = {
#         'name': app.config['APPLICATION_NAME'],
#         # 'short_name': app.config['APPLICATION_SHORT_NAME'],
#         # 'main_page_url': app.config['APPLICATION_MAIN_URL'],
#         # 'css_url'       : app.config.get ('APPLICATION_CSS_URL', ''),
#         # 'css': 'span.smalltext { font-size: smaller }',
#     }
#     return make_json_response(info)


# @app.errorhandler(404)
# def not_found(error):
#     return make_response(flask.jsonify({'error': 'Not found'}), 404)


# @app.endpoint('search')
# def search(dict_id):
#     headword = flask.request.args.get("headword")
#     entry = flask.request.args.get("entry")
#     query = flask.request.args.get("q")
#     query_type = flask.request.args.get("query_type")
#     input_translit = flask.request.args.get("input_translit")

#     # set term to default if not set
#     if query_type is None:
#         query_type = 'term'

#     if headword is not None:
#         # headword = transliterate_slp1_into_iso(headword, conv)
#         print(headword, query_type)
#         headword = urllib.parse.unquote(headword)
#         if input_translit == 'slp1':
#             res = get_from_elastic(dict_id, headword, query_type, 'headword_slp1')
#         if input_translit == 'iso':
#             res = get_from_elastic(dict_id, headword, query_type, 'headword_iso')
#         if input_translit == 'ascii':
#             res = get_from_elastic(dict_id, headword, query_type, 'headword_ascii')
#         if input_translit == 'deva':
#             res = get_from_elastic(dict_id, headword, query_type, 'headword_deva')
#         if input_translit == 'hk':
#             res = get_from_elastic(dict_id, headword, query_type, 'headword_hk')
#         if input_translit == 'gra':
#             if dict_id == 'gra':
#                 res = get_from_elastic(dict_id, headword, query_type, 'headword_gra')
#             else:
#                 return make_response(flask.jsonify({'error': 'Transliterarion not available for this dictionary'}), 404)

#     if entry is not None:
#         print(entry, query_type)
#         entry = urllib.parse.unquote(entry)
#         entry = entry.lower()
#         res = get_from_elastic(dict_id, entry, query_type, 'entry_tei_iso')

#     # default search
#     if query is not None:
#         query = urllib.parse.unquote(query)
#         '''
#         q = Q('bool',
#               should=[Q(query_type, headword_iso=query),
#                       Q(query_type, entry_tei_iso=query)],
#               minimum_should_match=1)
#         '''
#         res = client.search(index=dict_id,
#                             body={
#                                 "query": {
#                                     "bool": {
#                                         "should": [
#                                             {query_type: {
#                                                 "headword_iso": query
#                                             }},
#                                             {query_type: {
#                                                 "entry_tei_iso": query
#                                             }}
#                                         ],
#                                         "minimum_should_match": 1
#                                     }}})
#     resp = make_json_response(select_from_elatic_response(res['hits']['hits']))
#     return resp


# @app.endpoint('headwords_id')
# def headwords_id(dict_id, _id):
#     res = client.search(index=dict_id,
#                         body={
#                             "query":
#                                 {"term":
#                                      {'sort_id': int(_id)}
#                                  }
#                         })
#     res = make_json_response(select_from_elatic_response(res['hits']['hits']))
#     print(res, file=sys.stderr)
#     return res


# @app.endpoint('headwords_id_context')
# def headwords_id_context(dict_id, _id):
#     limit = clip(arg('limit', str(MAX_RESULTS), re_integer_arg), 1, MAX_RESULTS)
#     gte = _id - limit
#     lte = _id + limit
#     if gte < 0:
#         gte = 0
#     size = lte - gte
#     res = client.search(index=dict_id,
#                         body={
#                             "from": 0, "size": size,

#                             "sort": [
#                                 {"sort_id": {"order": "asc"}}
#                             ],
#                             "query": {
#                                 "range": {
#                                     "sort_id": {
#                                         "gte": gte,
#                                         "lte": lte
#                                     }
#                                 }
#                             }
#                         })

#     resp = make_json_response(select_from_elatic_response(res['hits']['hits']))
#     return resp


# app.url_map = Map([
#     Rule('/v1', endpoint='info'),
#     Rule('/v1/search/<dict_id>', endpoint='search'),
#     Rule('/v1/headwords/<dict_id>/<int:_id>', endpoint='headwords_id'),
#     Rule('/v1/headwords/<dict_id>/<int:_id>/context', endpoint='headwords_id_context')
# ])


# def simple(env, resp):
#     resp(b'200 OK', [(b'Content-Type', b'application/json')])
#     return [b'C-SALT_REST_API']


# app.wsgi_app = DispatcherMiddleware(simple, {'/dicts/sa/rest': app.wsgi_app})

# if __name__ == '__main__':
#     app.config.update(
#         DEBUG=True)
#     app.run(host='127.0.0.1', port=os.environ.get('PORT', 5000))
