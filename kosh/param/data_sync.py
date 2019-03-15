from distutils.util import strtobool
from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod, instance, logger


class data_sync(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    instance.config.set('data', 'sync', str(strtobool(params[0])))
    logger().info('Set data sync to %r', bool(strtobool(params[0])))
