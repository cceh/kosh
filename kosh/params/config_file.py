import re
import sys

from configparser import ConfigParser

from kosh.utils import *
from kosh.params._param import _param

class config_file(_param):
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

    try: self.config.read_file(open(params[0]))
    except: sys.exit('Invalid config file: {}'.format(params[0]))
