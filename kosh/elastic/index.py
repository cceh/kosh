from configparser import ConfigParser
from glob import glob
from json import load, loads
from os import path
from typing import Any, Dict, Iterable, List

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
    bulk = [ntry.to_dict(include_meta = True) for ntry in entry(elex).parser()]
    logger().info('Adding %i items to elastic index %s', len(bulk), elex.uid)
    helpers.bulk(connections.get_connection(), bulk)

  @classmethod
  def create(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    logger().debug('Creating elastic index %s', elex.uid)
    indices = connections.get_connection().indices
    indices.create(index = elex.uid, body = cls.__schema(elex))

  @classmethod
  def delete(cls, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    logger().debug('Dropping elastic index %s', elex.uid)
    indices = connections.get_connection().indices
    indices.delete(ignore = 404, index = elex.uid)

  @classmethod
  def lookup(cls, root: str, spec: str) -> List[Dict[str, Any]]:
    '''
    todo: docs
    '''
    indices = []

    logger().debug('Looking for dict definitions in %s', root)
    for file in glob('{}/**/{}'.format(root, spec), recursive = True):
      try:
        indices += cls.__parser(file)
        logger().info('Found dict definition in %s', file)
      except:
        logger().warn('Corrupt dict definition in %s', file)

    return indices

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
  def worker(cls, root: str, spec: str) -> Iterable[Dict[str, Any]]:
    '''
    todo: docs
    '''
    from inotify.adapters import InotifyTree
    from inotify.constants import IN_CLOSE_WRITE

    task = InotifyTree(root, IN_CLOSE_WRITE)

    for _, _, part, _ in task.event_gen(yield_nones = False):
      file = '{}/{}'.format(part, spec)

      if path.isfile(file):
        logger().info('Observed change of dict %s', file)
        for elex in cls.__parser(file): yield elex

  @classmethod
  def __parser(cls, file: str) -> List[Dict[str, Any]]:
    '''
    todo: docs
    '''
    conf = ConfigParser()
    root = path.dirname(file)
    conf.read_file(open(file))

    indices = []

    for uid in conf.sections():
      files = ['{}/{}'.format(root, i) for i in loads(conf.get(uid, 'files'))]
      schema = load(open('{}/{}'.format(root, conf.get(uid, 'schema'))))
      indices += [dotdict({ 'uid': uid, 'files': files, 'schema': schema })]

    return indices

  @classmethod
  def __schema(cls, elex: Dict[str, Any]) -> Dict[str, Any]:
    '''
    todo: docs
    '''
    emap = elex.schema.mappings.entry.properties
    emap.created = { 'type': 'date' }
    emap.xml = { 'analyzer': 'strip_tags', 'type': 'text' }

    elex.schema.settings = {
      'analysis': {
        'analyzer': {
          'strip_tags': {
            'type': 'custom',
            'tokenizer': 'standard',
            'char_filter': ['html_strip'],
            'filter': ['standard', 'lowercase' ]
          }
        }
      }
    }

    return elex.schema
