import re
import sys

from configparser import ConfigParser

from kosh.utils import *
from kosh.params._param import _param

class config(_param):
  '''
  todo: docs
  '''

  @concretemethod
  def _parse(self, params: List[str]) -> None:
    '''
    todo: docs
    '''
    self.config = ConfigParser()
    self.config.read_dict(default_config)

    if re.match(r'^\[\w+\]', params[0]):
      try: self.config.read_string(params[0])
      except: sys.exit('Invalid config string: {}'.format(params[0]))
    else:
      try: self.config.read_file(open(params[0]))
      except: sys.exit('Invalid config file: {}'.format(params[0]))
