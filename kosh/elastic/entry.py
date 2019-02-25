from datetime import datetime
from hashlib import sha1
from typing import Any, Dict, List
from unicodedata import normalize

from elasticsearch_dsl import Document
from lxml import etree

from kosh.utils import dotdict, logger
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
    xmap = self.elex.schema.mappings.entry._meta._xpaths

    logger().debug('Parsing dictionary entries for %s', self.elex.uid)
    for file in self.elex.files:
      elem = etree.parse(file, etree.XMLParser(remove_blank_text = True))
      for item in elem.xpath(xmap.root, namespaces = ns()):
        docs += [self.__record(item)]

    logger().debug('Found %i entries for %s', len(docs), self.elex.uid)
    return docs

  def schema(self, *args, **kwargs) -> Document:
    '''
    todo: docs
    '''
    class entry(Document):
      class Index: name = self.elex.uid
      class Meta: doc_type = 'entry'

    emap = dotdict(self.elex.schema.mappings.entry.properties)
    for prop in emap: entry._doc_type.mapping.field(prop, emap[prop].type)

    return entry(*args, **kwargs)

  def __record(self, root: etree.Element) -> Document:
    '''
    todo: docs
    '''
    elem = etree.tostring(root, encoding = 'utf-8')
    xmap = dotdict(self.elex.schema.mappings.entry._meta._xpaths)
    find = lambda s: next(iter(root.xpath(s, namespaces = ns())), None)

    item = self.schema(
      meta = { 'id': find(xmap.id) or sha1(elem).hexdigest() },
      created = datetime.now(),
      xml = elem.decode('unicode_escape')
    )

    for prop in xmap.fields:
      data = find(xmap.fields[prop])
      if data is not None: item[prop] = normalize('NFC', data.text)

    return item
