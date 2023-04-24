from typing import Type

from flask import Flask
from flask_graphql import GraphQLView as ql
from graphene import (
    Boolean,
    DateTime,
    Enum,
    Float,
    Int,
    List,
    NonNull,
    ObjectType,
    Schema,
    String,
)

from ..elastic.search import search
from ..utility.concretemethod import concretemethod
from ..utility.dotdictionary import dotdictionary
from ..utility.instance import instance
from ..utility.logger import logger
from ._api import _api


class graphql(_api):
    """
    todo: docs
    """

    graphenemap = dotdictionary(
        {
            "boolean": Boolean,
            "date": DateTime,
            "float": Float,
            "integer": Int,
            "keyword": String,
            "short": Int,
            "text": String,
        }
    )

    @concretemethod
    def deploy(self, flask: Flask) -> None:
        """
        todo: docs
        """
        view = ql.as_view(self.path, schema=self.__schema(), graphiql=True)
        logger().debug("Deploying GraphQL endpoint %s", self.path)
        flask.add_url_rule(self.path, self.path, view, strict_slashes=False)

    def __schema(self) -> Schema:
        """
        todo: docs
        """
        lexicon = self.lexicon
        mapping = [(j, i) for i, j in enumerate(self.mapping)]
        typing = type(lexicon.uid, (ObjectType, object), self.__typing())
        query_types = [(j, i) for i, j in enumerate(instance.query_types)]

        class query(ObjectType):
            entries = List(
                typing,
                field=NonNull(Enum("field", mapping)),
                query=NonNull(String),
                query_type=NonNull(Enum("queryType", query_types)),
                size=Int(),
            )

            ids = List(typing, ids=List(NonNull(String)))

            def resolve_ids(self, _, ids):
                return search.ids(lexicon, ids)

            def resolve_entries(self, _, field, query, query_type, size=10):
                field = [i for i in mapping if i[1] == field][0][0]
                query_type = instance.query_types[query_type]
                return search.entries(lexicon, field, query, query_type, size)

        return Schema(query=query)

    def __typing(self) -> Type:
        """
        todo: docs
        """
        fields = self.lexicon.schema.mappings._meta._xpaths.fields
        typing = {}

        for property in self.mapping:
            array_like = "[{}]".format(property) in fields
            graphene = self.graphenemap[self.mapping[property].type]
            typing[property] = List(graphene) if array_like else graphene()

        return typing
