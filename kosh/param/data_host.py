from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class data_host(_param):
    """
    The Elasticsearch host kosh will use
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        instance.config.set("data", "host", params[0])
        logger().info("Set data host to %s", params[0])

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return instance.config.get("data", "host")
