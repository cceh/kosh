from typing import *

'''
Concretemethod annotation with typechecking.

This inheritance helper throws an error when an annotated concretemethod does
not correctly inherit its base methods signature.
'''
def concretemethod(call: Callable) -> Callable:
  from inspect import stack
  from re import search

  name = search(r'class[^(]+\((\w+)\)\:', stack()[2][4][0]).group(1)
  base = getattr(stack()[2][0].f_locals[name], call.__name__)

  if get_type_hints(call) != get_type_hints(base):
    raise(TypeError('Invalid concretisation'))

  return(call)

'''
Default kosh configuration
'''
default_config = {
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
    'file': '.%(name)s',
    'root': '/var/lib/%(name)s'
  },
  'info': {
    'desc': '%(name)s - APIs for Dictionaries',
    'link': 'https://kosh.uni-koeln.de',
    'mail': 'info@cceh.uni-koeln.de',
    'repo': 'https://github.com/cceh/kosh'
  }
}

'''
Custom type 'Param': Any class derived from the _param base class.
'''
param = Type['kosh.param._param._param']
