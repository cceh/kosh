from configparser import ConfigParser
from gc import collect
from glob import glob
from itertools import groupby
from json import load, loads
from os import path
from re import compile
from time import time
from typing import Any, Callable, Dict, List

from elasticsearch import helpers
from elasticsearch_dsl import connections

from ..utility.dotdictionary import dotdictionary
from ..utility.instance import instance
from ..utility.logger import logger
from .entry import entry
import traceback
from lxml import etree

class index:
    """
    todo: docs
    """

    @classmethod
    def append(cls, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        input = entry(lexicon)
        lexicon.size = 0
        
        for file in lexicon.files:
                    try:
                        bulk = (i.to_dict(include_meta=True) for i in input.parse(file))
                        size, _ = helpers.bulk(connections.get_connection(), bulk)
                        logger().debug("Read %i entries to index %s", size, lexicon.uid)
                        lexicon.size += size
                    except etree.XMLSyntaxError as xml_error:
                        logger().warn("Skipping corrupt dict XML at %s", file)
                        logger().warn("XML Error: %s", str(xml_error))
                    except etree.XPathEvalError as xpath_error:
                        logger().warn("XPath Error in file %s: %s", file, str(xpath_error))
                    except Exception as e:
                        logger().warn("Skipping due to unexpected error at %s", file)
                        logger().warn("Error: %s", str(e))
                        logger().warn("Traceback: %s", traceback.format_exc())

        collect()
        logger().info("Added %i entries to index %s", lexicon.size, lexicon.uid)

    @classmethod
    def create(cls, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        indices = connections.get_connection().indices
        logger().debug("Creating index %s", lexicon.uid)
        indices.create(index=lexicon.pool, body=cls.__schema(lexicon))

    @classmethod
    def delete(cls, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        indices = connections.get_connection().indices
        logger().debug("Dropping index %s", lexicon.uid)
        indices.delete(ignore=404, index=lexicon.pool)

    @classmethod
    def lookup(cls, root: str, spec: str) -> List[Dict[str, Any]]:
        """
        todo: docs
        """
        indices = []
        logger().debug("Looking for dict definitions in %s", root)

        for file in glob(f"{root}/**/{spec}", recursive=True):
            try:
                indices += cls.__parser(file)
            except Exception:
                logger().warn("Skipping corrupt dict definition in %s", file)

        return indices

    @classmethod
    def notify(cls, root: str, spec: str) -> Callable:
        """
        todo: docs
        """
        from inotify.adapters import InotifyTree
        from inotify.constants import IN_CLOSE_WRITE, IN_CREATE

        task = InotifyTree(root, IN_CLOSE_WRITE | IN_CREATE)
        unique = lambda value: (value[2], int(time() / 60))

        for tick, _ in groupby(task.event_gen(yield_nones=0), key=unique):
            file = f"{tick[0]}/{spec}"

            if ".git" not in file and path.isfile(file):
                logger().debug("Observed change in %s", tick[0])
                yield lambda lexicon=file: cls.__parser(lexicon)

    @classmethod
    def update(cls, lexicon: Dict[str, Any]) -> None:
        """
        todo: docs
        """
        logger().info("Updating index %s", lexicon.uid)

        cls.delete(lexicon)
        cls.create(lexicon)
        cls.append(lexicon)

    @classmethod
    def __parser(cls, file: str) -> List[Dict[str, Any]]:
        """
        todo: docs
        """
        pool = instance.config["data"]["pool"]
        root = path.dirname(file)
        spec = ConfigParser(converters={"value": cls.__value})

        spec.SECTCRE = compile(r"^\[(?P<header>[a-z][_a-z0-9]+)\]$")
        spec.read_file(open(file))

        return [
            dotdictionary(lexicon)
            for lexicon in [
                [
                    (
                        "uid",
                        uid,
                    ),
                    (
                        "pool",
                        f"{spec[uid].getvalue('pool', pool)}[{uid}]",
                    ),
                    (
                        "files",
                        [
                            f"{root}/{file}"
                            for file in spec[uid].getvalue("files")
                        ],
                    ),
                    (
                        "schema",
                        load(open(f"{root}/{spec[uid].getvalue('schema')}")),
                    ),
                    *[
                        (key, spec[uid].getvalue(key))
                        for key in spec.options(uid)
                        if key not in ["files", "pool", "schema"]
                    ],
                ]
                for uid in spec.sections()
            ]
        ]

    @classmethod
    def __schema(cls, lexicon: Dict[str, Any]) -> Dict[str, Any]:
        """
        todo: docs
        """
        mapping = lexicon.schema.mappings.properties
        mapping.created = {"type": "date"}
        mapping.xml = {"analyzer": "strip_tags", "type": "text"}
        lexicon.schema.mappings.properties = dotdictionary(mapping)

        lexicon.schema.settings = {
            "analysis": {
                "analyzer": {
                    "strip_tags": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "char_filter": ["html_strip"],
                        "filter": ["lowercase"],
                    },
                },
            },
        }

        return lexicon.schema

    @classmethod
    def __value(cls, value: str) -> Any:
        """
        todo: docs
        """
        try:
            return loads(value)
        except Exception:
            return value
