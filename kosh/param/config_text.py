from sys import exit
from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class config_text(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    try: instance.config.read_string(params[0])
    except: exit('Invalid config string {}'.format(params[0]))

    logger().info('Read config string %s', params[0])
