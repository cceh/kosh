from configparser import ConfigParser
from importlib import import_module
from logging import basicConfig, getLogger
from os import getpid
from sys import argv, exit

from elasticsearch_dsl import connections
from kosh.elastic.index import index
from kosh.utils import defaultconfig, logger, store


def main() -> None: kosh().main()
if __name__ == '__main__': main()

class kosh():
  '''
  todo: docs
  '''

  def __init__(self) -> None:
    '''
    todo: docs
    '''
    store().config = ConfigParser()
    store().config.read_dict(defaultconfig())

    basicConfig(
      datefmt = '%Y-%m-%d %H:%M:%S',
      format = '%(asctime)s [%(levelname)s] <%(name)s> %(message)s'
    )

  def main(self) -> None:
    '''
    todo: docs
    '''
    try:
      logger().info('Started with pid %s', getpid())
      self.__params()
      self.__initdb()
      self.__server()

    except Exception as exception: logger().exception(exception)
    except SystemExit as exception: logger().error(str(exception))

  def __initdb(self) -> None:
    '''
    todo: docs
    '''
    getLogger('elasticsearch').setLevel(99)
    host = store().config.get('data', 'host')
    link = connections.create_connection(hosts = [host])

    for idx in index.search():
      index.delete(link, idx.uid)
      index.create(link, idx)

  def __params(self) -> None:
    '''
    todo: docs
    '''
    params = argv[1:]
    for param in [i for i in params if i.startswith('--')]:
      module = '.'.join(__name__.split('.')[:-1] + ['params', param[2:]])
      try: module = list(import_module(module).__dict__.values())[-1]
      except: exit('Invalid parameter: {}'.format(param[2:]))
      module(params)

  def __server(self) -> None:
    '''
    todo: docs
    '''
    pass
