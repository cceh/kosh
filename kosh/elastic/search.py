from datetime import datetime
from re import split
from typing import Any, Dict, List

from elasticsearch_dsl import Search

from kosh.elastic.entry import entry
from kosh.utils import dotdict


class search():
  '''
  todo: docs
  '''

  @classmethod
  def ids(cls,
    elex: Dict[str, Any],
    ids: List[str]
  ) -> List[Dict[str, str]]:
    '''
    todo: docs
    '''
    query = entry(elex).schema()

    return [dotdict({
      **i.to_dict(),
      'id': i.meta.id
    }) for i in query.mget(ids)]

  @classmethod
  def entries(cls,
    elex: Dict[str, Any],
    field: str,
    query: str,
    query_type: str
  ) -> List[Dict[str, str]]:
    '''
    todo: docs
    '''
    query = Search(index = elex.uid).query(query_type, **{ field: query })

    return [dotdict({
      **i.to_dict(),
      'id': i.meta.id,
      'created': datetime(*map(int, split(r'\D', i.created)))
    }) for i in query.execute()]
