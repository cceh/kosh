from flask import Flask
from kosh.api._api import _api
from kosh.utils import concretemethod


class xquery(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, flsk: Flask) -> None:
    '''
    todo: docs
    '''
    pass
