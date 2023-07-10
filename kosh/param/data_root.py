from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class data_root(_param):
    """
    The path to XML lexical data with kosh files
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        instance.config.set("data", "root", params[0])
        logger().info("Set data root to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("data", "root")
