from sys import exit
from typing import List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class config_text(_param):
    """
    todo: docs
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        try:
            instance.config.read_string(params[0])
        except Exception:
            exit("Invalid config string {}".format(params[0]))

        logger().info("Read config string %s", params[0])
