from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class api_port(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    if not params[0].isdigit(): raise TypeError()
    instance.config.set('api', 'port', params[0])
    logger().info('Set api port to %s', params[0])
