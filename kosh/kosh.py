import os
import sys

from importlib import import_module

from kosh.utils import *

def main() -> None:
  params = []
  sys.argv.pop(0)

  for param in sys.argv:
    if param.startswith('--'):
      module = '.'.join(__name__.split('.')[:-1] + ['params', param[2:]])
      try: params.append(list(import_module(module).__dict__.values())[-1])
      except: sys.exit('Invalid parameter: {}'.format(param[2:]))

  for i, param in enumerate(params):
    try: params[i] = param(sys.argv)
    except SystemExit as exception: raise exception
    except: sys.exit('Invalid parameters for: {}'.format(param.__module__))

if __name__ == '__main__': main()
