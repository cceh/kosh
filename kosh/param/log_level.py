from logging import getLevelName
from sys import exit
from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class log_level(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    try: logger().setLevel(getLevelName(params[0]))
    except: exit('Invalid log level {}'.format(params[0]))

    instance.config.set('logs', 'elvl', params[0])
    logger().info('Set log level to %s', params[0])
