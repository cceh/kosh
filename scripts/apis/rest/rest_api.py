import json
import os
import re
import sys
import urllib.parse
import configparser
import flask
from elasticsearch import Elasticsearch
from flask import make_response
from indic_transliteration.xsanscript import SchemeMap, SCHEMES, HK, SLP1, DEVANAGARI
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import DispatcherMiddleware

client = Elasticsearch()
conf_parser = configparser.ConfigParser()
conf_path = r'../../../utils/rest.conf'
conf_parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), conf_path))

app = flask.Flask(__name__)
app.config["APPLICATION_ROOT"] = conf_parser.get('APP_INFO', 'APPLICATION_ROOT')
app.config["APPLICATION_NAME"] = conf_parser.get('APP_INFO', 'APPLICATION_NAME')

MAX_RESULTS = 100
re_integer_arg = re.compile(r'^[0-9]+$')

scheme_slp1_deva = SchemeMap(SCHEMES[SLP1], SCHEMES[DEVANAGARI])
scheme_slp1_hk = SchemeMap(SCHEMES[SLP1], SCHEMES[HK])


def clip(i, min_, max_):
    return max(min(int(i), max_), min_)


def arg(name, default, regex, msg=None):
    arg = flask.request.args.get(name, default)
    if not regex.match(arg):
        if msg is None:
            msg = 'Invalid %s parameter' % name
        flask.abort(msg)
    return arg


####


def make_json_response(obj):
    resp = flask.Response(json.dumps(obj, indent=2, ensure_ascii=False), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


def get_from_elastic(dict_id, query, query_type=None, field=None):
    if query_type == 'ids':
        res = client.search(index=dict_id,
                            body={
                                "query": {'ids': {'values': query}},
                                "sort": [
                                    {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                ]})
    else:
        if query_type == 'fuzzy':
            res = client.search(index=dict_id,
                                body={
                                    "query": {"fuzzy": {field: {"value": query,
                                                                "prefix_length": 1,
                                                                "fuzziness": 1}}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ]
                                })
        else:
            res = client.search(index=dict_id,
                                body={
                                    "query": {query_type: {field: query}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ]})
    return res


def select_from_elatic_response(elastic_raw):
    data = {}
    from_elastic = []
    for e in elastic_raw:
        elastic_result = {}
        elastic_result['id'] = e['_id']
        elastic_result['headword_iso'] = e['_source']['headword_iso']
        elastic_result['headword_slp1'] = e['_source']['headword_slp1']
        elastic_result['headword_hk'] = e['_source']['headword_hk']
        elastic_result['headword_deva'] = e['_source']['headword_deva']
        elastic_result['headword_ascii'] = e['_source']['headword_ascii']
        elastic_result['entry_tei_iso'] = e['_source']['entry_tei_iso']
        from_elastic.append(elastic_result)
    data['data'] = from_elastic
    return data


### here we go

@app.endpoint('info')
def info():
    """ Endpoint.  The root of the application. """

    info = {
        'name': app.config['APPLICATION_NAME'],
        # 'short_name': app.config['APPLICATION_SHORT_NAME'],
        # 'main_page_url': app.config['APPLICATION_MAIN_URL'],
        # 'css_url'       : app.config.get ('APPLICATION_CSS_URL', ''),
        # 'css': 'span.smalltext { font-size: smaller }',
    }
    return make_json_response(info)


@app.errorhandler(404)
def not_found(error):
    return make_response(flask.jsonify({'error': 'Not found'}), 404)


@app.endpoint('search')
def search(dict_id):
    headword = flask.request.args.get("headword")
    entry = flask.request.args.get("entry")
    query = flask.request.args.get("q")
    query_type = flask.request.args.get("query_type")
    input_translit = flask.request.args.get("input_translit")

    # set term to default if not set
    if query_type is None:
        query_type = 'term'

    if headword:
        # headword = transliterate_slp1_into_iso(headword, conv)
        print(headword, query_type)
        headword = urllib.parse.unquote(headword)
        if input_translit == 'slp1':
            res = get_from_elastic(dict_id, headword, query_type, 'headword_slp1')
        if input_translit == 'iso':
            res = get_from_elastic(dict_id, headword, query_type, 'headword_iso')
        if input_translit == 'ascii':
            res = get_from_elastic(dict_id, headword, query_type, 'headword_ascii')
        if input_translit == 'deva':
            res = get_from_elastic(dict_id, headword, query_type, 'headword_deva')
        if input_translit == 'hk':
            res = get_from_elastic(dict_id, headword, query_type, 'headword_hk')
        if input_translit == 'gra':
            if dict_id == 'gra':
                res = get_from_elastic(dict_id, headword, query_type, 'headword_gra')
            else:
                return make_response(flask.jsonify({'error': 'Transliterarion not available for this dictionary'}),
                                     404)

    if entry:
        print(entry, query_type)
        entry = urllib.parse.unquote(entry)
        entry = entry.lower()
        res = get_from_elastic(dict_id, entry, query_type, 'entry_tei_iso')

    # default search
    if query:
        query = urllib.parse.unquote(query)
        '''
        q = Q('bool',
              should=[Q(query_type, headword_iso=query),
                      Q(query_type, entry_tei_iso=query)],
              minimum_should_match=1)
        '''
        res = client.search(index=dict_id,
                            body={
                                "query": {
                                    "bool": {
                                        "should": [
                                            {query_type: {
                                                "headword_iso": query
                                            }},
                                            {query_type: {
                                                "entry_tei_iso": query
                                            }}
                                        ],
                                        "minimum_should_match": 1
                                    }}})

    if 'res' in locals():
        resp = make_json_response(select_from_elatic_response(res['hits']['hits']))

    else:
        info_input = {
            'you need to specify which type of query you want to execute!': 'see some examples in the documentation',
            "documentation's current URL": "https://hackmd.io/s/SJUgBEs9m"
        }
        resp = make_json_response(info_input)

    return resp


@app.endpoint('headwords_id')
def headwords_id(dict_id, _id):
    res = client.search(index=dict_id,
                        body={
                            "query":
                                {"term":
                                     {'sort_id': int(_id)}
                                 }
                        })
    res = make_json_response(select_from_elatic_response(res['hits']['hits']))
    print(res, file=sys.stderr)
    return res


@app.endpoint('headwords_id_context')
def headwords_id_context(dict_id, _id):
    limit = clip(arg('limit', str(MAX_RESULTS), re_integer_arg), 1, MAX_RESULTS)
    gte = _id - limit
    lte = _id + limit
    if gte < 0:
        gte = 0
    size = lte - gte
    res = client.search(index=dict_id,
                        body={
                            "from": 0, "size": size,

                            "sort": [
                                {"sort_id": {"order": "asc"}}
                            ],
                            "query": {
                                "range": {
                                    "sort_id": {
                                        "gte": gte,
                                        "lte": lte
                                    }
                                }
                            }
                        })

    resp = make_json_response(select_from_elatic_response(res['hits']['hits']))
    return resp


app.url_map = Map([
    Rule('/v1', endpoint='info'),
    Rule('/v1/search/<dict_id>', endpoint='search'),
    Rule('/v1/headwords/<dict_id>/<int:_id>', endpoint='headwords_id'),
    Rule('/v1/headwords/<dict_id>/<int:_id>/context', endpoint='headwords_id_context')
])


def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'application/json')])
    return [b'C-SALT_REST_API']


app.wsgi_app = DispatcherMiddleware(simple, {'/dicts/sa/rest': app.wsgi_app})

if __name__ == '__main__':
    app.config.update(
        DEBUG=True)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5000))
