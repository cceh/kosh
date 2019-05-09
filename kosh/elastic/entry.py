from datetime import datetime
from hashlib import sha1
from re import search
from typing import Any, Dict, List
from unicodedata import normalize

from elasticsearch_dsl import Document
from lxml import etree

from kosh.utils import logger
from kosh.utils import namespaces as ns


class entry():
  '''
  todo: docs
  '''

  def __init__(self, elex: Dict[str, Any]) -> None:
    '''
    todo: docs
    '''
    self.elex = elex

  def parser(self) -> List[Document]:
    '''
    todo: docs
    '''
    docs = []
    xmap = self.elex.schema.mappings._meta._xpaths

    logger().debug('Parsing dictionary entries for %s', self.elex.uid)
    for file in self.elex.files:
      elem = etree.parse(file, etree.XMLParser(remove_blank_text = True))
      for item in elem.xpath(xmap.root, namespaces = ns()):
        docs += [self.__record(item)]

    logger().info('Found %i entries for %s', len(docs), self.elex.uid)
    return docs

  def schema(self, *args, **kwargs) -> Document:
    '''
    todo: docs
    '''
    class entry(Document):
      class Index: name = self.elex.uid

    emap = self.elex.schema.mappings.properties
    for i in emap: entry._doc_type.mapping.field(i, emap[i].type)

    return entry(*args, **kwargs)

  def __record(self, root: etree.Element) -> Document:
    '''
    todo: docs
    '''
    elem = etree.tostring(root, encoding = 'unicode')
    xmap = self.elex.schema.mappings._meta._xpaths
    euid = next(iter(root.xpath(xmap.id, namespaces = ns())), None) \
      or sha1(elem.encode('utf-8')).hexdigest()

    item = self.schema(
      meta = { 'id': euid },
      created = datetime.now(),
      xml = elem
    )

    for prop in xmap.fields:
      for data in root.xpath(xmap.fields[prop], namespaces = ns()):
        if data is not None and data.text is not None:
          data = normalize('NFC', data.text)
          if not search(r'^\[.*\]$', prop): item[prop] = data
          elif prop[1:-1] in item: item[prop[1:-1]] = [*item[prop[1:-1]], data]
          else: item[prop[1:-1]] = [data]

    return item
