from typing import List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class api_port(_param):
    """
    todo: docs
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
