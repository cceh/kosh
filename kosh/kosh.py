from configparser import ConfigParser
from importlib import import_module
from logging import basicConfig, getLogger
from os import environ, getpid
from pkgutil import iter_modules
from signal import pause
from sys import argv, exit
from threading import Thread

from elasticsearch_dsl import connections
from flask import Flask

from kosh.elastic.index import index
from kosh.utils import defaultconfig, dotdict, instance, logger

basicConfig(
  datefmt = '%Y-%m-%d %H:%M:%S',
  format = '%(asctime)s [%(levelname)s] <%(name)s> %(message)s'
)

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
    instance.config = ConfigParser()
    instance.config.read_dict(defaultconfig())

    instance.server = Flask(instance.config.get('api', 'name'))
    instance.server.config['PROPAGATE_EXCEPTIONS'] = True

  def main(self) -> None:
    '''
    todo: docs
    '''
    try:
      logger().info('Started kosh with pid %s', getpid())
      self.__params()
      self.__readdb()
      self.__update()
      self.__websrv()
      pause()

    except KeyboardInterrupt: print('\N{bomb}')
    except Exception as exception: logger().exception(exception)
    except SystemExit as exception: logger().critical(str(exception))

    finally: logger().info('Stopped kosh with pid %s', getpid())

  def __params(self) -> None:
    '''
    todo: docs
    '''
    params = argv[1:]
    for param in [i for i in params if i.startswith('--')]:
      module = '.'.join(__name__.split('.')[:-1] + ['params', param[2:]])
      try: module = import_module(module).__dict__[param[2:]]
      except: exit('Invalid parameter: {}'.format(param[2:]))
      module(params)

  def __readdb(self) -> None:
    '''
    todo: docs
    '''
    data = dotdict(instance.config['data'])
    mods = [i for _, i, _ in iter_modules(['kosh/api']) if not i[0] is ('_')]
    apis = [import_module('kosh.api.{}'.format(i)).__dict__[i] for i in mods]

    getLogger('elasticsearch').disabled = True
    connections.create_connection(hosts = [data.host])

    for elex in index.lookup(data.root, data.spec):
      for api in apis: api(elex).deploy(instance.server)
      index.update(elex)

  def __update(self) -> None:
    '''
    todo: docs
    '''
    class thread(Thread):
      def run(self) -> None:
        data = dotdict(instance.config['data'])
        logger().info('Starting data sync in %s', data.root)
        for elex in index.worker(data.root, data.spec): index.update(elex)

    if instance.config.getboolean('data', 'sync'):
      thread(daemon = True).start()

  def __websrv(self) -> None:
    '''
    todo: docs
    '''
    class thread(Thread):
      def run(self) -> None:
        api = dotdict(instance.config['api'])
        logger().info('Starting kosh server on %s:%s', api.host, api.port)
        instance.server.run(host = api.host, port = api.port)

    environ['WERKZEUG_RUN_MAIN'] = 'true'
    getLogger('werkzeug').disabled = True
    thread(daemon = True).start()
