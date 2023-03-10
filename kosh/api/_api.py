from abc import ABC, abstractmethod
from typing import Any, Dict

from flask import Flask

from ..utility.dotdictionary import dotdictionary
from ..utility.instance import instance


class _api(ABC):
    """
    Abstract protected api class.

    It provides the base class to extend when implementing dictionary APIs.
    """

    @abstractmethod
    def deploy(self, flask: Flask) -> None:
        """
        todo: docs
        """
        raise NotImplementedError("Too abstract")

    def __init__(self, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        self.config = dotdictionary(instance.config["api"])
        self.lexicon = lexicon

        self.mapping = dotdictionary(
            {
                "id": {"type": "keyword"},
                **self.lexicon.schema.mappings.properties,
                "created": {"type": "date"},
                "xml": {"type": "text"},
            }
        )

        self.path = "{}/{}/{}".format(
            self.config.root,
            self.lexicon.uid,
            self.__class__.__name__.split(".")[-1],
        )
