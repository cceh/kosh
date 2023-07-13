from logging import FileHandler, getLogger
from sys import exit
from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class log_file(_param):
    """
    Specifies the the file kosh will log to
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        if instance.config.get("logger", "file"):
            raise TypeError()

        try:
            handler = FileHandler(params[0], "a")
            handler.setFormatter(getLogger().handlers[0].formatter)
            getLogger().addHandler(handler)
        except Exception:
            exit(f"Invalid log file {params[0]}")

        instance.config.set("logger", "file", params[0])
        logger().info("Set log file to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("logger", "file")
