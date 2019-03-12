from sys import exit
from typing import List

from kosh.param._param import _param
from kosh.utils import concretemethod


class help(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    exit('Work in progress')
