from inspect import getmodule, stack
from logging import Logger, getLevelName, getLogger

from ..utility.dotdictionary import dotdictionary
from ..utility.instance import instance


def logger() -> Logger:
    """
    ``logger`` method, returning a ``Logger`` instance for the caller with the
    current logger level set. The preferred logger functionality throughout this
    application.

    :returns: A ``Logger`` instance for the caller.
    """
    config = dotdictionary(instance.config["logger"])
    source = getLogger(getmodule(stack()[1].frame).__name__)
    source.setLevel(getLevelName(config.level))

    return source
