from abc import ABC, abstractmethod
from importlib import import_module

from kosh.utils import *

# new
import flask

class _api(ABC):
  '''
  Abstract protected api class.

  It provides the base class to extend when implementing dictionary APIs.
  '''

  @abstractmethod
  def register(self, endpoint: object) -> None:
    '''
    todo: docs
    '''
    raise(NotImplementedError('Too abstract'))
