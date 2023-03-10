from sys import exit
from typing import List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class config_file(_param):
    """
    todo: docs
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        try:
            instance.config.read_file(open(params[0]))
        except Exception:
            exit("Invalid config file {}".format(params[0]))

        logger().info("Read config file %s", params[0])
