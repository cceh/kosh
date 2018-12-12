import os
import configparser
import requests
import git
from elastic import index_tei

conf_parser = configparser.ConfigParser()
conf_path = r'../../utils/github_listener.conf'
conf_parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), conf_path))

repo_dir = conf_parser.get('PATHS', 'REPO_DIR')
ssh_executable = conf_parser.get('PATHS', 'SSH_EXEC')
repo_dir = conf_parser.get('PATHS', 'REPO_DIR')
gra_tei = conf_parser.get('PATHS', 'gra_tei')
bhs_tei = conf_parser.get('PATHS', 'bhs_tei')
ap90_tei = conf_parser.get('PATHS', 'ap90_tei')
vei_tei = conf_parser.get('PATHS', 'vei_tei')

repo = git.Repo(repo_dir)


def get_file_name(path_to_file):
    file_name = path_to_file.split('/')
    file_name = file_name[-1]
    return file_name


files_to_index = (get_file_name(gra_tei), get_file_name(bhs_tei), get_file_name(ap90_tei), get_file_name(vei_tei))


def re_index_files(payload):
    with repo.git.custom_environment(GIT_SSH=ssh_executable):
        o = repo.remotes.origin
        o.pull()
    # check which files have been updated and then reindex them
    # merged_by = ['pull_request']['merged_by']
    sha = payload['pull_request']['head']['sha']
    commits_url = payload['pull_request']['head']['repo']['commits_url']
    commits_url = commits_url.replace('{/sha}', '/' + sha)
    req = requests.get(commits_url)
    commits_json = req.json()
    files = commits_json['files']
    re_indexed = []
    for file in files:
        filename = file['filename']
        filename = filename.split('/')
        filename = filename[-1]
        # logger.info(filename)
        if filename in files_to_index:
            re_indexed.append(filename)
            # reindex files
            index_tei.del_and_re_index(filename.replace('.tei', ''),
                                       conf_parser.get('PATHS', filename.replace('.', '_')),
                                       conf_parser.get('PATHS', 'slp1_iso_mapping'))
    return re_indexed
