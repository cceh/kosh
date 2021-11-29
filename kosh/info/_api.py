from abc import ABC, abstractmethod
from typing import Any, Dict

from flask import Flask

from kosh.utils import dotdict, instance


class _api(ABC):
  '''
  Abstract protected api class.

  It provides the base class to extend when implementing dictionary APIs.
  '''

  @abstractmethod
  def deploy(self, wapp: Flask) -> None:
    '''
    todo: docs
    '''
    raise(NotImplementedError('Too abstract'))

  def __init__(self) -> None:
    '''
    todo: docs
    '''
    self.conf = dotdict(instance.config['api'])

    self.path = '{}/{}'.format(
      self.conf.root,
      'info'
    )
