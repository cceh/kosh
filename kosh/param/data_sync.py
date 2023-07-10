from distutils.util import strtobool
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
        instance.config.set("data", "sync", str(strtobool(params[0])))
        logger().info("Set data sync to %r", bool(strtobool(params[0])))

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("data", "sync")
