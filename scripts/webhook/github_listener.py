import configparser
import json
import logging
import os
import git
import requests
from elastic import index_tei
from elasticsearch import Elasticsearch
from flask import Flask, Response, request, jsonify
from redis import Redis
from rq import Queue
from werkzeug.wsgi import DispatcherMiddleware
from reindex import re_index_files

client = Elasticsearch()
conf_parser = configparser.ConfigParser()
conf_path = r'../../utils/github_listener.conf'
conf_parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), conf_path))


app = Flask(__name__)

redis_conn = Redis()
q = Queue(connection=redis_conn)
logging.basicConfig(filename='wh_logger.log', level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger('server').setLevel(level=logging.INFO)
logger = logging.getLogger('server')

app.config["APPLICATION_NAME"] = conf_parser.get('APP_INFO', 'APPLICATION_NAME')


def make_json_response(obj):
    resp = Response(json.dumps(obj, indent=2, ensure_ascii=False), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/')
def home():
    """ Endpoint.  The root of the application. """
    info = {
        'name': app.config['APPLICATION_NAME'],
    }
    return make_json_response(info)


@app.route("/payload", methods=['POST'])
def github_payload():
    logger.info('incoming payload')
    if request.headers.get('X-GitHub-Event') == "ping":
        return jsonify({'msg': 'Ok'})
    if request.headers.get('X-GitHub-Event') == "pull_request":
        logger.info('incoming pull_request')
        payload = request.get_json()
        if payload:
            if payload['action'] == 'closed':
                logger.info('action = closed')
                merged_status = payload['pull_request']['merged']
                if merged_status == True:
                    logger.info('reindex = started')

                    q.enqueue(
                        re_index_files, payload)
                    logger.info('reindex = started')
                    return jsonify({'msg': 'indexed!'})

    return jsonify({'msg': 'Nothing happened :)'})


def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'C-SALT Github Listener']


app.wsgi_app = DispatcherMiddleware(simple, {'/dicts/github-webhooks': app.wsgi_app})

if __name__ == '__main__':
    app.config.update(
        DEBUG=True,
        JSON_AS_ASCII=False)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5010))
