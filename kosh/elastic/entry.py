from datetime import datetime
from hashlib import sha1
from os import path
from re import search
from typing import Any, Dict, List
from unicodedata import normalize

from elasticsearch_dsl import Document
from lxml import etree

from ..utility.instance import instance
from ..utility.logger import logger


class entry:
    """
    todo: docs
    """

    def __init__(self, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        self.lexicon = lexicon

    def parse(self, file: str) -> List[Document]:
        filename = path.basename(file)
        namespaces = {**instance.config._sections["namespaces"]}
        namespaces = {prefix: uri for prefix, uri in namespaces.items() if uri}

        xpaths = self.lexicon.schema.mappings._meta._xpaths

        logger().debug("Parsing file %s/%s", self.lexicon.uid, filename)
        tree = etree.parse(file, etree.XMLParser(remove_blank_text=True))

        for element in tree.xpath(xpaths.root, namespaces=namespaces):
            yield self.__record(element, namespaces)


    def schema(self, *args, **kwargs) -> Document:
        """
        todo: docs
        """

        class entry(Document):
            class Index:
                name = self.lexicon.pool

        for property in self.lexicon.schema.mappings.properties:
            entry._doc_type.mapping.field(
                property,
                self.lexicon.schema.mappings.properties[property].type,
            )

        return entry(*args, **kwargs)

    def __record(self, root: etree.Element, namespaces) -> Document:
        """
        todo: docs
        """
        element = etree.tostring(root, encoding="unicode")
        namespaces = {**instance.config._sections["namespaces"]}
        xpaths = self.lexicon.schema.mappings._meta._xpaths

        for name in root.xpath(xpaths.id, namespaces=namespaces) or [None]:
            if isinstance(name, etree._Element) and name.text is not None:
                name = normalize("NFC", name.text)
            elif isinstance(name, etree._ElementUnicodeResult):
                name = normalize("NFC", name)
            else:
                name = sha1(element.encode("utf-8")).hexdigest()

        item = self.schema(
            meta={"id": name},
            created=datetime.now(),
            xml=element,
        )

        for field in xpaths.fields:
            for node in root.xpath(xpaths.fields[field], namespaces=namespaces):
                if isinstance(node, etree._Element) and node.text is not None:
                    node = normalize("NFC", node.text)
                elif isinstance(node, etree._ElementUnicodeResult):
                    node = normalize("NFC", node)
                else:
                    node = None

                if node is not None:
                    if not search(r"^\[.*\]$", field):
                        item[field] = node
                    elif field[1:-1] in item:
                        item[field[1:-1]] = [*item[field[1:-1]], node]
                    else:
                        item[field[1:-1]] = [node]

        root.clear()
        return item
