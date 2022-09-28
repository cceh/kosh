from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class data_pool(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    instance.config.set('data', 'pool', params[0])
    logger().info('Set data pool to %s', params[0])
