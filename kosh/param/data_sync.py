from distutils.util import strtobool
from typing import List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class data_sync(_param):
    """
    todo: docs
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        instance.config.set("data", "sync", str(strtobool(params[0])))
        logger().info("Set data sync to %r", bool(strtobool(params[0])))
