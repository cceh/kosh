from typing import Type

from flask import Flask
from flask_graphql import GraphQLView as ql
from graphene import Enum, Int, List, NonNull, ObjectType, Schema, String

from kosh.api._api import _api
from kosh.elastic.search import search
from kosh.utils import concretemethod, graphenemap, logger, querytypes


class graphql(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, wapp: Flask) -> None:
    '''
    todo: docs
    '''
    view = ql.as_view(self.path, schema = self.__schema(), graphiql = True)
    logger().debug('Deploying GraphQL endpoint %s', self.path)

    wapp.add_url_rule(self.path, view_func = view)

  def __schema(self) -> Schema:
    '''
    todo: docs
    '''
    elex = self.elex
    emap = [(j, i) for i, j in enumerate(self.emap)]
    etyp = type(elex.uid, (ObjectType, object), self.__typing())

    class query(ObjectType):
      entries = List(
        etyp,
        field = NonNull(Enum('field', emap)),
        query = NonNull(String),
        query_type = NonNull(Enum.from_enum(querytypes)),
        size = Int()
      )

      ids = List(
        etyp,
        ids = List(NonNull(String))
      )

      def resolve_ids(self, _, ids):
        return search.ids(elex, ids)

      def resolve_entries(self, _, field, query, query_type, size = 10):
        field = next(i for i in emap if i[1] == field)[0]
        query_type = querytypes(query_type).name
        return search.entries(elex, field, query, query_type, size)

    return Schema(query = query)

  def __typing(self) -> Type:
    '''
    todo: docs
    '''
    fmap = self.elex.schema.mappings._meta._xpaths.fields
    tmap = {}

    for prop in self.emap:
      gmap = graphenemap()[self.emap[prop].type]
      if '[{}]'.format(prop) in fmap: tmap[prop] = List(gmap)
      else: tmap[prop] = gmap()

    return tmap
