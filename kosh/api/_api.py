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
  def deploy(self, flask: Flask) -> None:
    '''
    todo: docs
    '''
    raise(NotImplementedError('Too abstract'))

  def __init__(self, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    self.elex = elex

    self.emap = dotdict({
      'id': { 'type': 'keyword' },
      **elex.schema.mappings.entry.properties,
      'created': { 'type': 'date' },
      'xml': { 'type': 'text' }
    })

    self.path = '{}/{}/{}'.format(
      instance.config.get('api', 'root'),
      elex.uid,
      self.__class__.__name__.split('.')[-1]
    )
