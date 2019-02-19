from importlib import import_module
from inspect import getmodule, stack
from logging import Logger, getLevelName, getLogger
from re import search
from typing import Callable, Dict, List, Union, get_type_hints

from graphene import Boolean, Float, Int, String


def concretemethod(method: Callable) -> Callable:
  '''
  ``concretemethod`` annotation with typechecking.

  This inheritance helper throws an error when an annotated concretemethod does
  not correctly inherit its base methods signature.

  Param ``method``<``Callable``>:
    The annotated method.
  Return<``Callable``>:
    The passed in method.
  '''
  name = search('class[^(]+\((\w+)\)\:', stack()[2][4][0]).group(1)
  base = getattr(stack()[2][0].f_locals[name], method.__name__)

  if get_type_hints(method) != get_type_hints(base):
    raise(TypeError('Invalid concretisation'))

  return(method)

class dotdict(dict):
  '''
  ``dict`` wrapper to allow dot-operator access to values.
  See: https://stackoverflow.com/a/23689767
  '''
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

def defaultconfig() -> Dict[str, Dict[str, str]]:
  '''
  ``defaultconfig`` method, returning the default kosh configuration as dotdict.
  Should be passed to ``ConfigParser.read_dict`` to define sane default values.

  Return<``Dict[str, Dict[str, str]]``>:
    A dotdict containing the default configuration.
  '''
  return dotdict({
    'DEFAULT': {
      'name': 'kosh'
    },
    'api': {
      'ipv4': '0.0.0.0',
      'ipv6': '::/0',
      'port': 5000,
      'root': '/api'
    },
    'data': {
      'host': 'localhost',
      'file': '.%(name)s',
      'root': '/var/lib/%(name)s'
    },
    'info': {
      'desc': '%(name)s - APIs for Dictionaries',
      'link': 'https://kosh.uni-koeln.de',
      'mail': 'info@cceh.uni-koeln.de',
      'repo': 'https://github.com/cceh/kosh'
    },
    'logs': {
      'elvl': 'INFO'
    }
  })

def graphenemap() -> Dict[str, Union[Boolean, Float, Int, String]]:
  '''
  ``graphenemap`` method, returning the Elastic to Graphene type mapping as
  dotdict, containing Elastic types as string keys and Graphene types as values.

  Return<``Dict[str, Union[Boolean, Float, Int, String]]``>:
    A dotdict containing the Elastic to Graphene type mapping.
  '''
  return dotdict({
    'keyword': String,
    'text': String,
    'short': Int,
    'integer': Int,
    'float': Float,
    'boolean': Boolean
  })

def logger() -> Logger:
  '''
  ``logger`` method, returning a Logger instance for the caller with the current
  loglevel set. The preferred logging functionality throughout this application.

  Return<``Logger``>:
    A Logger instence for the caller.
  '''
  instance = getLogger(getmodule(stack()[1].frame).__name__)
  instance.setLevel(getLevelName(store().config.get('logs', 'elvl')))
  return instance

def store() -> Dict[any, any]:
  '''
  ``store`` method, returning a dotdict sigleton. This singleton data store,
  shared throughout kosh, is the runtime-storage for all components.

  Return<``Dict[any, any]``>
    The dotdict singleton.
  '''
  if not 'entity' in globals():
    global entity
    entity = dotdict()

  return entity
