from configparser import ConfigParser
from glob import glob
from json import load, loads
from os import path
from typing import Any, Dict, Iterable, List

from elasticsearch_dsl import connections
from inotify.adapters import InotifyTree
from inotify.constants import IN_CLOSE_WRITE

from kosh.utils import dotdict, logger


class index():
  '''
  todo: docs
  '''

  @classmethod
  def create(cls, elex: object) -> None:
    '''
    todo: docs
    '''
    logger().info('Creating elastic index %s', elex.uid)
    indices = connections.get_connection().indices
    indices.create(index = elex.uid, body = elex.schema)

  @classmethod
  def delete(cls, name: str) -> None:
    '''
    todo: docs
    '''
    logger().info('Dropping elastic index %s', name)
    indices = connections.get_connection().indices
    indices.delete(ignore = 404, index = name)

  @classmethod
  def lookup(cls, root: str, spec: str) -> List[Dict[str, Any]]:
    '''
    todo: docs
    '''
    indices = []

    logger().debug('Looking for dicts definitions in %s', root)
    for file in glob('{}/**/{}'.format(root, spec), recursive = True):
      try:
        indices += cls.__parser(file)
        logger().debug('Found dict definition in %s', file)
      except:
        logger().warn('Corrupt dict definition in %s', file)

    return indices

  @classmethod
  def worker(cls, root: str, spec: str) -> Iterable[Dict[str, Any]]:
    '''
    todo: docs
    '''
    task = InotifyTree(root, IN_CLOSE_WRITE)

    for (_, _, part, _) in task.event_gen(yield_nones = False):
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

  # @classmethod
  # def __notify(cls) -> None:
  #   file = instance.config.get('data', 'file')
  #   root = instance.config.get('data', 'root')
  #   tree = InotifyTree(root, IN_CLOSE_WRITE)

  #   try:
  #     for (_, _, path, item) in tree.event_gen(yield_nones = False):
  #       if path.isfile('{}/{}'.format(path, file)):
  #         print('path:' + str(path))
  #         print('file:' + str(file))

  #   except:
  #     print('exception')
