from typing import Any

from ..utility.dotdictionary import dotdictionary


class instance:
    """
    ``instance`` class, containing a dotdictionary singleton.

    This singleton instance, shared throughout kosh, is the runtime-storage for
    all components.
    """

    __instance = dotdictionary()

    @classmethod
    def __getattr__(cls, attr: str) -> Any:
        """
        ``__getattr__`` method, returning the associated value for the supplied
        key from the dotdictionary instance singleton.

        :param attr: The key who's associated value shall be returned.
        :returns: The value associated with the supplied key.
        """
        return cls.__instance[attr]

    @classmethod
    def __setattr__(cls, attr: str, value: Any) -> None:
        """
        ``__setattr__`` method, setting the value for the supplied key on the
        dotdictionary instance singleton.

        :param attr: The key to be set.
        :returns: The value to be associated with the supplied key.
        """
        cls.__instance[attr] = value

    @classmethod
    def __delattr__(cls, attr: str) -> None:
        """
        ``__delattr__`` method, removing a key and its associated value from the
        dotdictionary instance singleton.

        :param attr: The key to be removed.
        """
        del cls.__instance[attr]
