from datetime import datetime
from inspect import stack
from json import dumps
from typing import Any, Dict, List

from flask import Flask, Response, request
from flask_swagger_ui import get_swaggerui_blueprint

from kosh.api._api import _api
from kosh.elastic.search import search
from kosh.utils import concretemethod, instance, logger, querytypes, swaggermap


class restful(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, wapp: Flask) -> None:
    '''
    todo: docs
    '''
    path = lambda p: '{}/{}'.format(self.path, p)
    logger().debug('Deploying RESTful endpoint %s', self.path)

    wapp.add_url_rule(path('entries'), path('entries'), self.entries)
    wapp.add_url_rule(path('ids'), path('ids'), self.ids)
    wapp.add_url_rule(path('spec'), path('spec'), self.spec)

    wapp.register_blueprint(get_swaggerui_blueprint(
      self.path,
      path('spec'),
      blueprint_name = self.elex.uid,
      config = { 'layout': 'BaseLayout' }
    ), url_prefix = self.path)

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
    query = request.args.get('query')
    query_type = request.args.get('query_type')

    if not query:
      return self.__fail('Missing query parameter')
    if not field in self.emap:
      return self.__fail('Missing or invalid field parameter')
    if not query_type in [i.name for i in querytypes]:
      return self.__fail('Missing or invalid query_type parameter')

    return self.__data(search.entries(self.elex, field, query, query_type))

  def spec(self) -> Response:
    '''
    todo: docs
    '''
    def param(name):
      return {
        'name': name,
        'in': 'query',
        'required': True,
        'type': 'string'
      }

    def props(item):
      return {
        'properties': {
          'data': {
            'properties': {
              item: {
                'type': 'array',
                'items': { '$ref': '#/definitions/Entry' }
              }
            }
          }
        }
      }

    def reply(dref):
      return {
        '200': {
          'description': 'Matching dictionary entries',
          'schema': { '$ref': '#/definitions/{}'.format(dref) }
        },
        '400': {
          'description': 'Missing or invalid parameter'
        }
      }

    return self.__json({
      'swagger': '2.0',
      'host': request.host,
      'basePath': self.path,
      'info': {
        'version': '1.0.0',
        'title': instance.config.get('info', 'desc')
      },
      'tags': [{ 'name': self.elex.uid }],
      'paths': {
        '/entries': {
          'get': {
            'tags': [self.elex.uid],
            'parameters': [
              { **param('field'), 'enum': list(self.emap.keys()) },
              { **param('query') },
              { **param('query_type'), 'enum': [i.name for i in querytypes] }
            ],
            'responses': reply('Entries')
          }
        },
        '/ids': {
          'get': {
            'tags': [self.elex.uid],
            'parameters': [{
              **param('ids'),
              'type': 'array',
              'collectionFormat': 'multi',
              'items': { 'type': 'string' }
            }],
            'responses': reply('Ids')
          }
        }
      },
      'definitions': {
        'Entry': {
          'properties': {
            **{ k: swaggermap()[self.emap[k].type] for k in self.emap.keys() },
            'xml': { 'type': 'string', 'format': 'xml' }
          }
        },
        'Entries': props('entries'),
        'Ids': props('ids')
      }
    })

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
