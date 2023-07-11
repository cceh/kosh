from importlib import import_module, metadata
from os import _exit, path
from pkgutil import iter_modules
from typing import Any, List

from ..utility.concretemethod import concretemethod
from ..utility.instance import instance
from ..utility.logger import logger
from ._param import _param


class help(_param):
    """
    Show this help and list available parameters
    """

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        summary = metadata.metadata("kosh").get("summary")
        print(summary + "\n" + len(summary) * "-")

        root = path.dirname(__file__)
        modules = [i for _, i, _ in iter_modules([root]) if i[0] != ("_")]
        logger().debug("Found param modules %s", modules)

        param_maxlen = max(map(len, modules))
        print("\nParameters:")

        for module in modules:
            param = import_module(f"kosh.param.{module}").__dict__[module]
            value = param._value(param)

            print(
                f"    --{module:<{param_maxlen}} ",
                param.__doc__.strip().split("\n")[0],
                f"(set to: {value})" if value else "",
            )

        module_maxlen = max(map(len, [i.__name__ for i in instance.modules]))
        print("\nLoaded API endpoint modules:")

        for module in instance.modules:
            print(
                f"    {module.__name__:<{module_maxlen}} -",
                module.__doc__.strip().split("\n")[0],
            )

        _exit(0)

    @concretemethod
    def _value(self) -> Any:
        """
        todo: docs
        """
        return None
