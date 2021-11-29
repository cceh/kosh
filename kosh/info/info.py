from datetime import datetime
from inspect import stack
from json import dumps
from typing import Any, Dict, List

from flask import Flask, Response

from kosh.info._api import _api
from kosh.elastic.search import search
from kosh.utils import concretemethod, logger


class info_restful(_api):
  '''
  todo: docs
  '''
  def __init__(self,data_list: List):
    super().__init__()
    self.data = data_list

  @concretemethod
  def deploy(self, wapp: Flask) -> None:
    '''
    todo: docs
    '''
    logger().debug('Deploying RESTful endpoint %s', self.path)
    path = lambda p: '{}/{}'.format(self.path, p)

    wapp.add_url_rule(path('dicts'),path('dicts'),self.dicts_view)

  def append_dict(self,data_dict:dict) ->None:
    '''
    Appends new dictionary to the data list
    '''
    self.data.append(data_dict)

  def dicts_view(self)-> Response:
    '''
    todo: docs
    '''
    logger().debug('dicts_view has been called\n{}'.format(self.data))
    return self.__data(self.data)

  def _count(self) -> Response:
    '''
    todo: docs
    '''
    return self.__data(search.dict_count(self.elex))

  def __data(self, body: List[Dict[str, str]]) -> Response:
    '''
    todo: docs
    '''
    return self.__json({ 'data': { stack()[1].function: body } })

  def __fail(self, body: str, code: int = 400) -> Response:
    '''
    combines the body string and an error code (default 400) into a ``__json`` function call. 
    '''
    return self.__json({ 'error': body }, code)

  def __json(self, body: Any, code: int = 200) -> Response:
    '''
    returns a json formated string as a flask ``response``
    '''
    return Response(
      dumps(body, default = self.__time, ensure_ascii = False),
      headers = { 'Content-Type': 'application/json; charset=utf-8' },
      mimetype = 'application/json',
      status = code
    )

  def __time(self, body: Any) -> str:
      '''
      todo: docs
      '''
      if isinstance(body, datetime): return body.isoformat()
      raise TypeError('Type {} not serializable'.format(type(body)))
