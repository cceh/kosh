from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class data_sync(_param):
    """
    The interval in which files are checked for changes
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        if not params[0].isdigit():
            raise TypeError()

        instance.config.set("data", "sync", params[0])
        logger().info("Set data sync to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("data", "sync")
