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
    find = entry(elex).schema()

    try: return [dotdict({
      **item.to_dict(),
      'id': item.meta.id
    }) for item in find.mget(ids)]
    except: return []

  @classmethod
  def entries(cls,
    elex: Dict[str, Any],
    field: str,
    query: str,
    query_type: str,
    size: int
  ) -> List[Dict[str, str]]:
    '''
    todo: docs
    '''
    find = Search(index = elex.pool).query(query_type, **{
      field if field != 'id' else '_id': query
    })

    try: return [dotdict({
      **item.to_dict(),
      'id': item.meta.id,
      'created': datetime(*map(int, split(r'\D', item.created)))
    }) for item in find[:size].execute()]
    except: return []
