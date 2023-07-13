from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class api_port(_param):
    """
    The port kosh will listen on
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        if not params[0].isdigit():
            raise TypeError()

        instance.config.set("api", "port", params[0])
        logger().info("Set api port to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("api", "port")
