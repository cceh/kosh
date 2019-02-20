from sys import exit
from typing import List

from kosh.params._param import _param
from kosh.utils import concretemethod, logger, instance


class config_file(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    try: instance.config.read_file(open(params[0]))
    except: exit('Invalid config file {}'.format(params[0]))

    logger().info('Read config file %s', params[0])
