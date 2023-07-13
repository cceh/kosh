from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class api_root(_param):
    """
    The API context path kosh will serve
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        if not params[0].startswith("/"):
            raise TypeError()

        instance.config.set("api", "root", params[0])
        logger().info("Set api root to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("api", "root")
