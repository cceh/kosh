from inspect import stack
from json import dumps
from typing import Any, Dict, List

from flask import Flask, Response, request

from kosh.api._api import _api
from kosh.elastic.search import search
from kosh.utils import concretemethod, logger, querytypes


class restful(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, flask: Flask) -> None:
    '''
    todo: docs
    '''
    path = lambda p: '{}/{}'.format(self.path, p)
    logger().info('Deploying RESTful endpoint %s', self.path)

    flask.add_url_rule(self.path, self.path, self.info)
    flask.add_url_rule(path('entries'), path('entries'), self.entries)
    flask.add_url_rule(path('ids'), path('ids'), self.ids)

  def info(self) -> Response:
    '''
    todo: docs
    '''
    return self.__json({
      'dict': self.elex.uid,
      'fields': self.emap,
      'query_types': [i.name for i in querytypes]
    })

  def ids(self) -> Response:
    '''
    todo: docs
    '''
    ids = request.args.getlist('ids')

    if not ids:
      return self.__fail('Missing parameter: ids')

    return self.__data(search.ids(self.elex, ids))

  def entries(self) -> Response:
    '''
    todo: docs
    '''
    field = request.args.get('field')
    query_type = request.args.get('query_type')
    query = request.args.get('query')

    if not field in self.emap:
      return self.__fail('Missing or invalid parameter: field')
    if not query_type in [i.name for i in querytypes]:
      return self.__fail('Missing or invalid parameter: query_type')
    if not query:
      return self.__fail('Missing parameter: query')

    return self.__data(search.entries(self.elex, field, query, query_type))

  def __data(self, body: List[Dict[str, str]]) -> Response:
    '''
    todo: docs
    '''
    return self.__json({ 'data': { stack()[1].function: body } })

  def __fail(self, body: str, code: int = 400) -> Response:
    '''
    todo: docs
    '''
    return self.__json({ 'error': body }, code)

  def __json(self, body: Any, code: int = 200) -> Response:
    '''
    todo: docs
    '''
    return Response(
      dumps(body, ensure_ascii = False),
      headers = { 'Content-Type': 'application/json; charset=utf-8' },
      mimetype = 'application/json',
      status = code
    )
