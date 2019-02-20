from configparser import ConfigParser
from importlib import import_module
from logging import basicConfig, getLogger
from os import getpid, path
from sys import argv, exit
from threading import Thread

from elasticsearch_dsl import connections

from kosh.elastic.entry import entry
from kosh.elastic.index import index
from kosh.utils import defaultconfig, dotdict, instance, logger


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

    basicConfig(
      datefmt = '%Y-%m-%d %H:%M:%S',
      format = '%(asctime)s [%(levelname)s] <%(name)s> %(message)s'
    )

  def main(self) -> None:
    '''
    todo: docs
    '''
    logger().info('Started kosh with pid %s', getpid())

    try:
      self.__params()
      self.__initdb()
      self.__notify()
      self.__server()

    except KeyboardInterrupt: print('\N{bomb}')
    except Exception as exception: logger().exception(exception)
    except SystemExit as exception: logger().critical(str(exception))
    finally: logger().info('Stopped kosh with pid %s', getpid())

  def __initdb(self) -> None:
    '''
    todo: docs
    '''
    data = dotdict(instance.config['data'])

    getLogger('elasticsearch').setLevel(99)
    connections.create_connection(hosts = [data.host])

    for elex in index.lookup(data.root, data.spec):
      index.delete(elex.uid)
      index.create(elex)
      for ntry in entry(elex).parser(): ntry.save()

  def __notify(self) -> None:
    class thread(Thread):
      def run(self) -> None:
        data = dotdict(instance.config['data'])
        for elex in index.worker(data.root, data.spec):
          index.delete(elex.uid)
          index.create(elex)
          for ntry in entry(elex).parser(): ntry.save()

    thread(daemon = True).start()

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
    from time import sleep
    sleep(5)
    input('kosh is served')
