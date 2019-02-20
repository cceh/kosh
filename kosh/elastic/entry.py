from datetime import datetime
from hashlib import sha256
from typing import Any, Dict
from unicodedata import normalize

from elasticsearch_dsl import (Boolean, Date, Document, Float, Integer,
                               Keyword, Text)
from lxml import etree

from kosh.utils import dotdict, logger
from kosh.utils import namespaces as ns


class entry():
  '''
  todo: docs
  '''

  uid = Keyword()
  created = Date()

  # headword_ascii = Keyword()
  # headword_deva = Keyword()
  # headword_hk = Keyword()
  # headword_iso = Keyword()
  # headword_slp1 = Keyword()

  def __init__(self, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    self.elex = elex

  def parser(self) -> None:
    '''
    todo: docs
    '''
    docs = []
    xmap = self.elex.schema.mappings.entry._meta._xpaths

    logger().info('Parsing dictionary entries for %s', self.elex.uid)
    for file in self.elex.files:
      for item in etree.parse(file).xpath(xmap.root, namespaces = ns()):
        docs += [self.__record(item)]

    logger().debug('Found %i entries for %s', len(docs), self.elex.uid)
    return docs

  def __record(self, root: etree.Element) -> Document:
    class entry(Document):
      class Meta: doc_type = 'entry'
      created = Date()

    emap = self.elex.schema.mappings.entry.properties
    xmap = self.elex.schema.mappings.entry._meta._xpaths
    find = lambda s: next(iter(root.xpath(s, namespaces = ns())), None)

    item = entry(meta = {
      'id': find(xmap.id) or sha256(etree.tostring(root)),
      'index': self.elex.uid
    })

    item.created = datetime.now()

    for prop in emap: item._doc_type.mapping.field(prop, {
      'boolean': Boolean,
      'date': Date,
      'float': Float,
      'integer': Integer,
      'keyword': Keyword,
      'text': Text
    }[emap[prop].type]())

    for prop in xmap.fields:
      data = find(xmap.fields[prop])
      if data is not None: item[prop] = normalize('NFC', data.text)

    return item
