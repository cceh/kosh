from distutils.util import strtobool
from logging import FileHandler, Formatter, getLogger
from sys import exit
from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class log_file(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    if instance.config.get('logs', 'file'): raise TypeError()

    try:
      handler = FileHandler(params[0], 'a')
      handler.setFormatter(getLogger().handlers[0].formatter)
      getLogger().addHandler(handler)
    except: exit('Invalid log file {}'.format(params[0]))

    instance.config.set('logs', 'file', params[0])
    logger().info('Set log file to %s', params[0])
