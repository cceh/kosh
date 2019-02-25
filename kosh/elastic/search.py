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
    entries = entry(elex).schema().mget(ids)

    return [dotdict({
      **i.to_dict(),
      'id': i.meta.id,
      'created': i.created.isoformat()
    }) for i in entries]

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
    search = Search(index = elex.uid).query(query_type, **{ field: query })

    return [dotdict({
      **i.to_dict(),
      'id': i.meta.id
    }) for i in search.execute()]
