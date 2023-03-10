from logging import getLevelName
from sys import exit
from typing import List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class log_level(_param):
    """
    todo: docs
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        try:
            logger().setLevel(getLevelName(params[0]))
        except Exception:
            exit("Invalid log level {}".format(params[0]))

        instance.config.set("logger", "level", params[0])
        logger().info("Set log level to %s", params[0])
