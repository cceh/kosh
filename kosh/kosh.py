from configparser import ConfigParser
from distutils.util import strtobool
from gc import collect
from importlib import import_module as mod
from logging import basicConfig, getLogger
from multiprocessing import Process
from os import environ, getpid, path
from pkgutil import iter_modules
from queue import Empty, Queue
from signal import pause
from sys import argv, exit
from threading import Thread
from time import sleep

from elasticsearch_dsl import connections
from flask import Flask
from flask_cors import CORS

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
    argv.pop(0)
    basicConfig(
      datefmt = '%Y-%m-%d %H:%M:%S',
      format = '%(asctime)s [%(levelname)s] <%(name)s> %(message)s'
    )
    environ['WERKZEUG_RUN_MAIN'] = 'true'
    getLogger('elasticsearch').disabled = True
    getLogger('werkzeug').disabled = True

  def main(self) -> None:
    '''
    todo: docs
    '''
    try:
      instance.config = ConfigParser()
      instance.config.read_dict(defaultconfig())
      logger().info('Started kosh with pid %s', getpid())

      root = '{}/{}'.format(path.dirname(__file__), 'api')
      mods = [i for _, i, _ in iter_modules([root]) if not i[0] is ('_')]
      instance.echoes = [mod('kosh.api.{}'.format(i)).__dict__[i] for i in mods]
      logger().info('Loaded API endpoint modules %s', mods)

      for i in [i for i in argv if i.startswith('--')]:
        try: mod('kosh.param.{}'.format(i[2:])).__dict__[i[2:]](argv)
        except: exit('Invalid parameter or argument to {}'.format(i[2:]))

      conf = dotdict(instance.config['data'])
      connections.create_connection(hosts = [conf.host])
      instance.elexes = { i.uid: i for i in index.lookup(conf.root, conf.spec) }
      for elex in instance.elexes.values(): index.update(elex)

      self.serve()
      self.watch() if strtobool(conf.sync) else pause()

    except KeyboardInterrupt: print('\N{bomb}')
    except Exception as exception: logger().exception(exception)
    except SystemExit as exception: logger().critical(str(exception))

    finally: logger().info('Stopped kosh with pid %s', getpid())

  def serve(self) -> None:
    '''
    todo: docs
    '''
    conf = dotdict(instance.config['api'])
    wapp = Flask(conf.name)
    CORS(wapp)
    wapp.config['PROPAGATE_EXCEPTIONS'] = True

    for elex in instance.elexes.values():
      for echo in instance.echoes: echo(elex).deploy(wapp)

    class process(Process):
      def run(self) -> None:
        logger().info('Deploying web server at %s:%s', conf.host, conf.port)
        wapp.run(host = conf.host, port = conf.port)

    try:
      instance.server.terminate()
      instance.server.join()
      collect()
    except: pass

    instance.server = process(daemon = True, name = 'server')
    instance.server.start()

  def watch(self) -> None:
    '''
    todo: docs
    '''
    conf = dotdict(instance.config['data'])
    tick = Queue()

    def lexer(elex):
      instance.elexes[elex.uid] = elex
      index.update(elex)
      self.serve()

    class thread(Thread):
      def run(self) -> None:
        logger().info('Starting data sync in %s', conf.root)
        for call in index.notify(conf.root, conf.spec): tick.put(call)

    thread(daemon = True, name = 'update').start()

    while True:
      try: [lexer(i) for i in tick.get(False)()]
      except Empty: sleep(1)
