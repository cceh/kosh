from flask import Flask
from flask_graphql import GraphQLView as ql
from graphene import Int, List, ObjectType, Schema, String
from kosh.api._api import _api
from kosh.utils import concretemethod, graphenemap, logger


class graphql(_api):
  '''
  todo: docs
  '''

  @concretemethod
  def deploy(self, flsk: Flask) -> None:
    '''
    todo: docs
    '''
    view = ql.as_view(self.path, schema = self.__schema(), graphiql = True)
    logger().info('Deploying GraphQL endpoint %s', self.path)
    flsk.add_url_rule(self.path, view_func = view)

  def __schema(self) -> None:
    '''
    todo: docs
    '''
    elex = type(
      self.elex.uid,
      (ObjectType, object),
      { prop: graphenemap()[self.emap[prop].type]() for prop in self.emap }
    )

    class query(ObjectType):
      entries = List(
        elex,
        field = String(),
        query = String(),
        query_type = String(),
        size = Int()
      )

      ids = List(
        elex,
        ids = List(String)
      )

      def resolve_ids(self, info, ids):
        print(info, ids)
        return []

      def resolve_entries(self, info, field, query, query_type, size):
        print(info, field, query, query_type, size)
        return []

    return Schema(query = query)
