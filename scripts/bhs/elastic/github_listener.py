import os
from flask import Flask, Response, request, jsonify
import json
from elasticsearch import Elasticsearch
from werkzeug.wsgi import DispatcherMiddleware
import git
import logging
from logging.handlers import RotatingFileHandler

client = Elasticsearch()

app = Flask(__name__)

app.config["APPLICATION_ROOT"] = "/dicts/github-webhooks"
app.config["APPLICATION_NAME"] = "GITHUB_LISTENER"

repo_dir = ("/home/fmondaca/dev/gra/dicts")
ssh_executable = '/home/fmondaca/dev/gra/ssh_exec.sh'


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
    # signature = request.headers.get('X-Hub-Signature')
    data = request.data
    if request.headers.get('X-GitHub-Event') == "ping":
        return jsonify({'msg': 'Ok'})
    if request.headers.get('X-GitHub-Event') == "pull_request":
        payload = request.get_json()
        if payload['action'] == 'closed':
            merged_status = ['pull_request']['merged']
            if merged_status == 'true':
                g = git.cmd.Git(repo_dir)
                g.pull()
    if request.headers.get('X-GitHub-Event') == "push":
        repo = git.Repo(repo_dir)
        with repo.git.custom_environment(GIT_SSH=ssh_executable):
            o = repo.remotes.origin
            o.pull()
    return data


def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'Hello WSGI World']


app.wsgi_app = DispatcherMiddleware(simple, {'/dicts/github-webhooks': app.wsgi_app})

if __name__ == '__main__':
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('webhooks.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.config.update(
        DEBUG=True,
        JSON_AS_ASCII=False)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5010))
