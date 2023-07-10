from logging import getLevelName
from sys import exit
from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class log_level(_param):
    """
    Specifies the kosh logger level
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        try:
            logger().setLevel(getLevelName(params[0]))
        except Exception:
            exit(f"Invalid log level {params[0]}")

        instance.config.set("logger", "level", params[0])
        logger().info("Set log level to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("logger", "level")
