from importlib import import_module
from sys import argv, exit
from os import path
from typing import List
from pkgutil import iter_modules

from ..utility.concretemethod import concretemethod
from ..utility.logger import logger
from ._param import _param


class help(_param):
    """
    Show help and list commands
    """

    @staticmethod
    def get_param_values(name, argv) -> List[str]:
        values = []
        found = False
        for arg in argv:
            if arg == f"--{name}":
                found = True
                continue
            elif arg.startswith("--") and found:
                break
            if found:
                values.append(arg)
        return values

    @concretemethod
    def _parse(self, params: List[str]) -> None:
        """
        todo: docs
        """
        modules = [
            i
            for _, i, _ in iter_modules([path.dirname(__file__)])
            if i[0] != ("_")
        ]
        logger().debug("Found param modules %s", modules)

        print("Parameters:")
        maxlen = max(map(len, modules))
        for module in modules:
            param_cls = import_module("kosh.param.{}".format(module)).__dict__[
                module
            ]
            values = self.get_param_values(module, argv)
            userval = (
                ", set to '{}'".format(", ".join(values)) if values else ""
            )
            print(
                f"    --{module:<{maxlen}}  {param_cls.__doc__.strip()}{userval}"
            )

        exit(0)
