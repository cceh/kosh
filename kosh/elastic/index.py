from configparser import ConfigParser
from glob import glob
from itertools import groupby
from json import load, loads
from os import path
from time import time
from typing import Any, Callable, Dict, List

from elasticsearch import helpers
from elasticsearch_dsl import connections

from kosh.elastic.entry import entry
from kosh.utils import dotdict, logger


class index():
  '''
  todo: docs
  '''

  @classmethod
  def append(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    bulk = [i.to_dict(include_meta = True) for i in entry(elex).parser()]
    logger().debug('Adding %i items to elastic index %s', len(bulk), elex.uid)
    helpers.bulk(connections.get_connection(), bulk)

  @classmethod
  def create(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    idxs = connections.get_connection().indices
    logger().debug('Creating elastic index %s', elex.uid)
    idxs.create(index = elex.uid, body = cls.__schema(elex))

  @classmethod
  def delete(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    idxs = connections.get_connection().indices
    logger().debug('Dropping elastic index %s', elex.uid)
    idxs.delete(ignore = 404, index = elex.uid)

  @classmethod
  def lookup(cls, root: str, spec: str) -> List[Dict[str, Any]]:
    '''
    todo: docs
    '''
    idxs = []

    logger().debug('Looking for dict definitions in %s', root)
    for file in glob('{}/**/{}'.format(root, spec), recursive = True):
      try: idxs += cls.__parser(file)
      except: logger().warn('Corrupt dict definition in %s', file)

    return idxs

  @classmethod
  def notify(cls, root: str, spec: str) -> Callable:
    '''
    todo: docs
    '''
    from inotify.adapters import InotifyTree
    from inotify.constants import IN_CLOSE_WRITE, IN_CREATE

    task = InotifyTree(root, IN_CLOSE_WRITE | IN_CREATE)
    uniq = lambda i: (i[2], int(time() / 60))

    for tick, _ in groupby(task.event_gen(yield_nones = 0), key = uniq):
      file = '{}/{}'.format(tick[0], spec)

      if not '.git' in file and path.isfile(file):
        logger().debug('Observed change in %s', tick[0])
        yield lambda i = file: cls.__parser(i)

  @classmethod
  def update(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    logger().info('Updating elastic index %s', elex.uid)
    cls.delete(elex)
    cls.create(elex)
    cls.append(elex)

  @classmethod
  def __parser(cls, file: str) -> List[Dict[str, Any]]:
    '''
    todo: docs
    '''
    conf = ConfigParser()
    root = path.dirname(file)
    conf.read_file(open(file))

    return [dotdict(elex) for elex in [[
      ('uid', uid),
      ('files', ['{}/{}'.format(root, i) for i in loads(conf[uid]['files'])]),
      ('schema', load(open('{}/{}'.format(root, conf[uid]['schema']))))
    ] for uid in conf.sections()]]

  @classmethod
  def __schema(cls, elex: Dict[str, Any]) -> Dict[str, Any]:
    '''
    todo: docs
    '''
    emap = elex.schema.mappings.properties
    emap.created = { 'type': 'date' }
    emap.xml = { 'analyzer': 'strip_tags', 'type': 'text' }
    elex.schema.mappings.properties = dotdict(emap)

    elex.schema.settings = {
      'analysis': {
        'analyzer': {
          'strip_tags': {
            'type': 'custom',
            'tokenizer': 'standard',
            'char_filter': ['html_strip'],
            'filter': ['lowercase' ]
          }
        }
      }
    }

    return elex.schema
