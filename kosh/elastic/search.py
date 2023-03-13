from datetime import datetime
from re import split
from typing import Any, Dict, List

from elasticsearch_dsl import Search

from .entry import entry


class search:
    """
    todo: docs
    """

    @classmethod
    def ids(
        cls,
        lexicon: Dict[str, Any],
        ids: List[str],
    ) -> List[Dict[str, str]]:
        """
        todo: docs
        """
        find = entry(lexicon).schema()

        try:
            return [{**i.to_dict(), "id": i.meta.id} for i in find.mget(ids)]
        except Exception:
            return []

    @classmethod
    def entries(
        cls,
        lexicon: Dict[str, Any],
        field: str,
        query: str,
        query_type: str,
        size: int,
    ) -> List[Dict[str, str]]:
        """
        todo: docs
        """
        find = Search(index=lexicon.pool).query(
            query_type, **{field if field != "id" else "_id": query}
        )

        try:
            return [
                {
                    **item.to_dict(),
                    "id": item.meta.id,
                    "created": datetime(*map(int, split(r"\D", item.created))),
                }
                for item in find[:size].execute()
            ]

        except Exception:
            return []
