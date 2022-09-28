from enum import Enum
from inspect import getmodule, stack
from logging import Logger, getLevelName, getLogger
from re import search
from typing import Any, Callable, Dict, Union, get_type_hints

from graphene import Boolean, DateTime, Float, Int, String


def concretemethod(method: Callable) -> Callable:
  '''
  ``concretemethod`` annotation with typechecking.

  This inheritance helper throws an error when an annotated concretemethod does
  not correctly inherit its base methods signature.

  Param ``method<Callable>``:
    The annotated method.
  Return``<Callable>``:
    The passed in method.
  '''
  name = search(r'class[^(]+\((\w+)\)\:', stack()[2][4][0]).group(1)
  base = getattr(stack()[2][0].f_locals[name], method.__name__)

  if get_type_hints(method) != get_type_hints(base):
    raise(TypeError('Invalid concretisation'))

  return(method)

class dotdict(dict):
  '''
  ``dotdict`` wrapper class to allow dot-operator access to ``dict`` values.

  See:
    https://stackoverflow.com/a/23689767
  And:
    https://stackoverflow.com/a/13520518
  '''
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

  def __init__(self, *args, **kwargs):
    for key, value in dict(*args, **kwargs).items():
      if hasattr(value, 'keys'): value = dotdict(value)
      self[key] = value

def defaultconfig() -> Dict[str, Dict[str, str]]:
  '''
  ``defaultconfig`` method, returning the default kosh configuration as dotdict.
  Should be passed to ``ConfigParser.read_dict`` to define sane default values.

  Return``<Dict[str, Dict[str, str]]>``:
    A dotdict containing the default configuration.
  '''
  return dotdict({
    'DEFAULT': {
      'name': 'kosh'
    },
    'api': {
      'host': '0.0.0.0',
      'port': 5000,
      'root': '/api'
    },
    'data': {
      'host': '127.0.0.1',
      'root': '/var/lib/%(name)s',
      'spec': '.%(name)s',
      'sync': True
    },
    'info': {
      'desc': '%(name)s - APIs for Lexical Data',
      'link': 'https://kosh.uni-koeln.de',
      'mail': 'info-kosh@uni-koeln.de',
      'repo': 'https://github.com/cceh/kosh'
    },
    'logs': {
      'elvl': 'INFO',
      'file': ''
    }
  })

def graphenemap() -> Dict[str, Union[Boolean, Float, Int, String]]:
  '''
  ``graphenemap`` method, returning the Elastic to Graphene type mapping as
  dotdict, containing Elastic types as string keys and Graphene types as values.

  Return``<Dict[str, Union[Boolean, Float, Int, String]]>``:
    A dotdict containing the Elastic to Graphene type mapping.
  '''
  return dotdict({
    'boolean': Boolean,
    'date': DateTime,
    'float': Float,
    'integer': Int,
    'keyword': String,
    'short': Int,
    'text': String
  })

def swaggermap() -> Dict[str, object]:
  '''
  ``swaggermap`` method, returning the Elastic to Swagger type mapping as
  dotdict, containing Elastic types as string keys and Swagger definitions as
  values.

  Return``<Dict[str, object]>``:
    A dotdict containing the Elastic to Swagger type mapping.
  '''
  return dotdict({
    'boolean': { 'type': 'boolean' },
    'date': { 'type': 'string', 'format': 'date-time' },
    'float': { 'type': 'number', 'format': 'float' },
    'integer': { 'type': 'integer' },
    'keyword': { 'type': 'string' },
    'short': { 'type': 'integer' },
    'text': { 'type': 'string' }
  })

def namespaces() -> Dict[str, str]:
  '''
  todo: docs
  '''
  return dotdict({
    'dc': 'http://purl.org/dc/elements/1.1',
    'tei': 'http://www.tei-c.org/ns/1.0'
  })

class instance():
  '''
  ``instance`` class, containing a dotdict sigleton. This singleton data
  storage, shared throughout kosh, is the runtime-storage for all components.
  '''
  __data = dotdict()

  @classmethod
  def __delattr__(cls, attr: str) -> None:
    '''
    ``__delattr__`` method, removing a key and its associated value from the
    dotdict data storage singleton.

    Param ``attr<str>``:
      The key to be removed.
    '''
    del cls.__data[attr]

  @classmethod
  def __getattr__(cls, attr: str) -> Any:
    '''
    ``__getattr__`` method, returning the associated value for the passed in
    key from the dotdict data storage singleton.

    Param ``attr<str>``:
      The key whos associated value shall be returned.
    Return<``Any``>:
      The value associated with the passed in key.
    '''
    return cls.__data[attr]

  @classmethod
  def __setattr__(cls, attr: str, value: Any) -> None:
    '''
    ``__setattr__`` method, setting the value for the passed in key on the
    dotdict data storage singleton.

    Param ``attr<str>``:
      The key to be set.
    Param ``value<Any>``:
      The value to be associated with the passed in key.
    '''
    cls.__data[attr] = value

def logger() -> Logger:
  '''
  ``logger`` method, returning a Logger instance for the caller with the current
  loglevel set. The preferred logging functionality throughout this application.

  Return<``Logger``>:
    A Logger instence for the caller.
  '''
  conf = dotdict(instance.config['logs'])
  unit = getLogger(getmodule(stack()[1].frame).__name__)
  unit.setLevel(getLevelName(conf.elvl))
  return unit

class querytypes(Enum):
  '''
  ``querytypes`` class extending Enum to implement an enumeration of allowed
  types of queries against the elasticsearch data host.

  To prevent easy crawling of the all datasets, disable the following entries:
  - ``prefix``
  - ``regex``
  - ``wildcard``
  '''
  term = 1
  fuzzy = 2
  terms = 3
  match = 4
  match_phrase = 5
  wildcard = 6
  regexp = 7
  prefix = 8
