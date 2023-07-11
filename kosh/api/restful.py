from datetime import datetime
from inspect import stack
from json import dumps
from typing import Any, Dict, List

from flask import Flask, Response, request
from flask_swagger_ui import get_swaggerui_blueprint
from pkg_resources import get_distribution

from ..elastic.search import search
from ..utility.concretemethod import concretemethod
from ..utility.dotdictionary import dotdictionary
from ..utility.instance import instance
from ..utility.logger import logger
from ._api import _api


class restful(_api):
    """
    A RESTful endpoint serving lexical data
    """

    swaggermap = dotdictionary(
        {
            "boolean": {"type": "boolean"},
            "date": {"type": "string", "format": "date-time"},
            "float": {"type": "number", "format": "float"},
            "integer": {"type": "integer"},
            "keyword": {"type": "string"},
            "short": {"type": "integer"},
            "text": {"type": "string"},
        }
    )

    @concretemethod
    def deploy(self, flask: Flask) -> None:
        """
        todo: docs
        """
        path = lambda endpoint: f"{self.path}/{endpoint}"
        logger().debug("Deploying RESTful endpoint %s", self.path)

        flask.add_url_rule(path("entries"), path("entries"), self.entries)
        flask.add_url_rule(path("ids"), path("ids"), self.ids)
        flask.add_url_rule(path("spec"), path("spec"), self.spec)

        flask.register_blueprint(
            get_swaggerui_blueprint(
                self.path,
                path("spec"),
                blueprint_name=self.lexicon.uid,
                config={"layout": "BaseLayout"},
            ),
            url_prefix=self.path,
        )

    def ids(self) -> Response:
        """
        todo: docs
        """
        ids = request.args.getlist("ids")

        if not ids:
            return self.__fail("Missing or invalid parameter: 'ids'")

        return self.__data(search.ids(self.lexicon, ids))

    def entries(self) -> Response:
        """
        todo: docs
        """
        field = request.args.get("field")
        query = request.args.get("query")
        query_type = request.args.get("query_type")
        size = int(request.args.get("size", 10))

        if not query:
            return self.__fail("Missing or invalid parameter: 'query'")
        if field not in self.mapping:
            return self.__fail("Missing or invalid parameter: 'field'")
        if query_type not in instance.query_types:
            return self.__fail("Missing or invalid parameter: 'query_type'")

        return self.__data(
            search.entries(self.lexicon, field, query, query_type, size)
        )

    def spec(self) -> Response:
        """
        todo: docs
        """

        def field(name):
            fields = self.lexicon.schema.mappings._meta._xpaths.fields
            swagger = self.swaggermap[self.mapping[name].type]

            return (
                swagger
                if not f"[{name}]" in fields
                else {"type": "array", "items": swagger}
            )

        def param(name):
            return {
                "name": name,
                "in": "query",
                "required": True,
                "type": "string",
            }

        def props(item):
            return {
                "properties": {
                    "data": {
                        "properties": {
                            item: {
                                "type": "array",
                                "items": {"$ref": "#/definitions/Entry"},
                            },
                        },
                    },
                },
            }

        def reply(name):
            return {
                "200": {
                    "description": "Matching dictionary entries",
                    "schema": {"$ref": f"#/definitions/{name}"},
                },
                "400": {"description": "Missing or invalid parameter"},
            }

        return self.__json(
            {
                "swagger": "2.0",
                "host": request.host,
                "basePath": self.path,
                "tags": [{"name": self.lexicon.uid}],
                "info": {
                    "title": instance.config["info"]["desc"],
                    "version": get_distribution("kosh").version,
                },
                "definitions": {
                    "Ids": props("ids"),
                    "Entries": props("entries"),
                    "Entry": {
                        "properties": {
                            **{i: field(i) for i in self.mapping.keys()},
                            "xml": {"type": "string", "format": "xml"},
                        },
                    },
                },
                "paths": {
                    "/entries": {
                        "get": {
                            "responses": reply("Entries"),
                            "tags": [self.lexicon.uid],
                            "parameters": [
                                {
                                    **param("field"),
                                    "enum": [*self.mapping.keys()],
                                },
                                {
                                    **param("query"),
                                    "type": "string",
                                },
                                {
                                    **param("query_type"),
                                    "enum": instance.query_types,
                                },
                                {
                                    **param("size"),
                                    "required": False,
                                    "type": "integer",
                                },
                            ],
                        },
                    },
                    "/ids": {
                        "get": {
                            "responses": reply("Ids"),
                            "tags": [self.lexicon.uid],
                            "parameters": [
                                {
                                    **param("ids"),
                                    "type": "array",
                                    "collectionFormat": "multi",
                                    "items": {"type": "string"},
                                },
                            ],
                        },
                    },
                },
            },
        )

    def __data(self, body: List[Dict[str, str]]) -> Response:
        """
        todo: docs
        """
        return self.__json({"data": {stack()[1].function: body}})

    def __fail(self, body: str, code: int = 400) -> Response:
        """
        todo: docs
        """
        return self.__json({"error": body}, code)

    def __json(self, body: Any, code: int = 200) -> Response:
        """
        todo: docs
        """

        def serialize(body):
            if isinstance(body, datetime):
                return body.isoformat()

            raise TypeError(f"Type {type(body)} not serializable")

        return Response(
            dumps(body, default=serialize, ensure_ascii=False),
            headers={"Content-Type": "application/json; charset=utf-8"},
            mimetype="application/json",
            status=code,
        )
