from abc import ABC, abstractmethod
from importlib import import_module

from kosh.utils import *

class _param(ABC):
  '''
  Abstract protected param class.

  It provides the base class to extend when implementing cli parameter parsers.
  '''

  def __init__(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    args = []
    params.pop(0)

    while params and not params[0].startswith('--'):
        args += [params.pop(0)]

    self._parse(args)

  @abstractmethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    raise(NotImplementedError('Too abstract'))
