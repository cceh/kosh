from abc import ABC, abstractmethod
from importlib import import_module
from typing import List

from kosh.utils import logger, store


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
    logger().debug('Parsing cli param %s', params.pop(0)[2:])
    while params and not params[0].startswith('--'): args += [params.pop(0)]
    logger().debug('Passing cli args %s', str(args))
    self._parse(args)

  @abstractmethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    raise(NotImplementedError('Too abstract'))
