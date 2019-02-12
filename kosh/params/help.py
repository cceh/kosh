import os

from kosh.utils import *
from kosh.params._param import _param

class help(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    print('Work in progress')
    os._exit(0)
