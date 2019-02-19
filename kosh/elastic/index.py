from configparser import ConfigParser
from glob import glob
from json import load, loads
from os import path
from typing import Dict, List, Union

from elasticsearch import Elasticsearch
from kosh.utils import dotdict, logger, store


class index():
  '''
  todo: docs
  '''

  def append(self, name: str) -> None:
    '''
    todo: docs
    '''
    pass

  @classmethod
  def create(self, link: Elasticsearch, spec: object) -> None:
    '''
    todo: docs
    '''
    logger().info('Creating elastic index %s', spec.uid)
    link.indices.create(index = spec.uid, body = spec.schema)

  @classmethod
  def delete(self, link: Elasticsearch, name: str) -> None:
    '''
    todo: docs
    '''
    logger().info('Dropping elastic index %s', name)
    link.indices.delete(ignore = 404, index = name)

  @classmethod
  def search(self) -> List[Dict[str, Union[object, str]]]:
    '''
    todo: docs
    '''
    file = store().config.get('data', 'file')
    root = store().config.get('data', 'root')
    logger().debug('Scanning for dicts in %s', root)

    items = []

    for spec in glob('{}/**/{}'.format(root, file), recursive = True):
      try: items += self.__format(spec)
      except: continue
      logger().debug('Found dict specification in %s', spec)

    return items

  @classmethod
  def __format(self, spec: str) -> List[Dict[str, Union[object, str]]]:
    '''
    todo: docs
    '''
    item = ConfigParser()
    root = path.dirname(spec)
    item.read_file(open(spec))

    items = []

    for uid in item.sections():
      file = item.get(uid, 'schema')
      items += [dotdict({
        'uid': uid,
        'files': loads(item.get(uid, 'files')),
        'schema': load(open('{}/{}'.format(root, file)))
      })]

    return items
