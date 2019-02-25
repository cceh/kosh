from flask import Flask
from flask_graphql import GraphQLView as ql
from graphene import Enum, List, NonNull, ObjectType, Schema, String

from kosh.api._api import _api
from kosh.elastic.search import search
from kosh.utils import concretemethod, graphenemap, logger, querytypes


class graphql(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, flask: Flask) -> None:
    '''
    todo: docs
    '''
    view = ql.as_view(self.path, schema = self.__schema(), graphiql = True)
    logger().info('Deploying GraphQL endpoint %s', self.path)
    flask.add_url_rule(self.path, view_func = view)

  def __schema(self) -> Schema:
    '''
    todo: docs
    '''
    elex = self.elex
    fields = [(j, i) for i, j in enumerate(self.emap)]
    typed_entry = type(
      elex.uid,
      (ObjectType, object),
      { prop: graphenemap()[self.emap[prop].type]() for prop in self.emap }
    )

    class query(ObjectType):
      entries = List(
        typed_entry,
        field = NonNull(Enum('field', fields)),
        query = NonNull(String),
        query_type = NonNull(Enum.from_enum(querytypes))
      )

      ids = List(
        typed_entry,
        ids = List(NonNull(String))
      )

      def resolve_ids(self, info, ids):
        return search.ids(elex, ids)

      def resolve_entries(self, info, field, query, query_type):
        field = next(i for i in fields if i[1] == field)[0]
        query_type = querytypes(query_type).name
        return search.entries(elex, field, query, query_type)

    return Schema(query = query)
