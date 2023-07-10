from sys import exit
from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class config_file(_param):
    """
    The configuration file kosh will use
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

        instance.config.set("DEFAULT", "conf", params[0])
        logger().info("Read config file %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("DEFAULT", "conf")
