import configparser
import json
import logging
import os
import git
import requests
from elastic import index_tei
from elasticsearch import Elasticsearch
from flask import Flask, Response, request, jsonify
from werkzeug.wsgi import DispatcherMiddleware

client = Elasticsearch()
conf_parser = configparser.ConfigParser()
conf_path = r'../../utils/github_listener.conf'
conf_parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), conf_path))

app = Flask(__name__)

app.config["APPLICATION_ROOT"] = conf_parser.get('APP_INFO', 'APPLICATION_ROOT')
app.config["APPLICATION_NAME"] = conf_parser.get('APP_INFO', 'APPLICATION_NAME')
repo_dir = conf_parser.get('PATHS', 'REPO_DIR')
ssh_executable = conf_parser.get('PATHS', 'SSH_EXEC')

gra_tei = conf_parser.get('PATHS', 'gra_tei')
bhs_tei = conf_parser.get('PATHS', 'bhs_tei')
ap90_tei = conf_parser.get('PATHS', 'ap90_tei')
vei_tei = conf_parser.get('PATHS', 'vei_tei')


def get_file_name(path_to_file):
    file_name = path_to_file.split('/')
    file_name = file_name[-1]
    return file_name


files_to_index = (get_file_name(gra_tei), get_file_name(bhs_tei), get_file_name(ap90_tei), get_file_name(vei_tei))


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
        if payload:
            print(payload)
            if payload['action'] == 'closed':
                merged_status = ['merged']
                if merged_status == 'true':
                    logging.log(logging.INFO, 'merged_status:  ' + merged_status)
                    g = git.cmd.Git(repo_dir)
                    g.pull()
                    logging.log(logging.INFO, 'c-salt_sanskrit_data pulled from upstream')
                    # check which files have been updated and then reindex them
                    # merged_by = ['pull_request']['merged_by']
                    sha = ['pull_request']['head']['sha']
                    commits_url = ['pull_request']['head']['repo']['commits_url']
                    commits_url = commits_url.replace('{/sha}', '/' + sha)
                    logging.log(logging.INFO, 'commits_url:   ' + commits_url)
                    req = requests.get(commits_url)
                    commits_json = json.loads(req.json)
                    files = commits_json['files']
                    for file in files:
                        #
                        filename = file['filename']
                        filename = filename.split['/']
                        filename = filename[-1]
                        logging.log(logging.INFO, filename)
                        if filename in files_to_index:
                            # reindex files
                            index_tei.del_and_re_index(filename.replace('.tei', ''),
                                                       conf_parser.get('PATHS', filename.replace('.', '_')),
                                                       conf_parser.get('PATHS', 'slp1_iso_mapping'))

    return data


def simple(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'C-SALT Github Listener']


app.wsgi_app = DispatcherMiddleware(simple, {'/dicts/github-webhooks': app.wsgi_app})

if __name__ == '__main__':
    logging.basicConfig(filename='wh_logger.log', level=logging.INFO)
    app.config.update(
        DEBUG=True,
        JSON_AS_ASCII=False)
    app.run(host='127.0.0.1', port=os.environ.get('PORT', 5010))
