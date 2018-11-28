import graphene
import json
from collections import namedtuple
from elasticsearch import Elasticsearch
from lxml import etree
from io import StringIO
from bs4 import BeautifulSoup

client = Elasticsearch()
namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    print(data)
    return json.loads(data, object_hook=_json_object_hook)


####################
# Schema for entries in elastic


parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

style = '''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ns="http://www.tei-c.org/ns/1.0" version="1.0"
  exclude-result-prefixes="ns">

 <xsl:output method="html"/>

  <xsl:template match="ns:entry">
    <div>
    <xsl:apply-templates select="ns:sense"/>
    </div>
   </xsl:template> 

   <xsl:template match="ns:sense">
   <xsl:apply-templates/>
   </xsl:template>

   <xsl:template match="ns:hi[@rendition='#b']">
   <b>
      <xsl:apply-templates/>
    </b>
   </xsl:template>

   <xsl:template match="ns:hi[@rendition='#i']">
   <i>
      <xsl:apply-templates/>
    </i>
   </xsl:template>


   <xsl:template match="ns:hi[@rendition='#wide']">
   <i>
      <xsl:apply-templates/>
    </i>
   </xsl:template>

   <xsl:template match="ns:w[@xml:lang='el']">
    <i>
      <xsl:apply-templates/>
    </i>
   </xsl:template>

   <xsl:template match="ns:w[@xml:lang='he']">
    <i>
      <xsl:apply-templates/>
    </i>
   </xsl:template>

   <xsl:template match="ns:lb">
      <br/>
   </xsl:template>

</xsl:stylesheet>
'''


def sense_as_html(entry_tei):
    tree = etree.parse(StringIO(entry_tei), parser)
    entry = tree.xpath('.')[0]
    xslt_root = etree.XML(style, parser)
    transform = etree.XSLT(xslt_root)
    f = StringIO(entry)
    doc = etree.parse(f)
    result_tree = transform(doc)
    return str(result_tree)


def extract_sense(entry_tei):
    tree = etree.parse(StringIO(entry_tei), parser)
    entry = tree.xpath('.')[0]
    entry_sense = entry.xpath('./ns:sense', namespaces=namespaces)[0]
    entry_sense = etree.tostring(entry_sense, encoding='unicode', pretty_print=True)
    soup = BeautifulSoup(entry_sense, 'lxml')
    entry_sense = soup.get_text()
    # remove \n
    entry_sense = entry_sense.replace('\n', '')
    return entry_sense


def select_from_elastic_response(elastic_raw):
    from_elastic = []
    for e in elastic_raw:
        elastic_result = {}
        elastic_result['id'] = e['_id']
        elastic_result['sort_id'] = e['_source']['sort_id']
        elastic_result['headword_iso'] = e['_source']['headword_iso']
        elastic_result['headword_slp1'] = e['_source']['headword_slp1']
        elastic_result['headword_hk'] = e['_source']['headword_hk']
        elastic_result['headword_deva'] = e['_source']['headword_deva']
        elastic_result['headword_ascii'] = e['_source']['headword_ascii']
        entry_tei_iso = e['_source']['entry_tei_iso']
        elastic_result['entry_tei_iso'] = entry_tei_iso
        elastic_result['sense_txt_iso'] = extract_sense(entry_tei_iso)
        elastic_result['sense_html_iso'] = sense_as_html(entry_tei_iso)
        from_elastic.append(elastic_result)
    return from_elastic


class GraEntry(graphene.ObjectType):
    id = graphene.String()
    sort_id = graphene.Int()
    headword_iso = graphene.String()
    headword_slp1 = graphene.String()
    headword_hk = graphene.String()
    headword_deva = graphene.String()
    headword_gra = graphene.String()
    headword_ascii = graphene.String()
    entry_tei_iso = graphene.String()
    entry_tei_gra = graphene.String()
    sense_txt_iso = graphene.String()
    sense_txt_gra = graphene.String()


class DictEntry(graphene.ObjectType):
    id = graphene.String()
    sort_id = graphene.Int()
    headword_iso = graphene.String()
    headword_slp1 = graphene.String()
    headword_hk = graphene.String()
    headword_deva = graphene.String()
    headword_ascii = graphene.String()
    entry_tei_iso = graphene.String()
    sense_txt_iso = graphene.String()
    sense_html_iso = graphene.String()


# queries

def get_from_elastic(dict_id, query, size=None, query_type=None, field=None):
    # set max size auf 100:
    if size is not None and size > 100:
        size = 100

    if query_type == 'ids':
        res = client.search(index=dict_id,
                            body={
                                "query": {'ids': {'values': query}},
                                "sort": [
                                    {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                ],
                                "from": 0, "size": size})
    else:
        if query_type == 'fuzzy':
            res = client.search(index=dict_id,
                                body={
                                    "query": {"fuzzy": {field: {"value": query,
                                                                "prefix_length": 1,
                                                                "fuzziness": 1}}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ]
                                    ,
                                    "from": 0, "size": size
                                })
        else:
            res = client.search(index=dict_id,
                                body={
                                    "query": {query_type: {field: query}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ],
                                    "from": 0, "size": size})
    return res


class DictQuery(graphene.ObjectType):
    entries = graphene.List(DictEntry, dict_id=graphene.String(), query=graphene.String(), query_type=graphene.String(),
                            field=graphene.String(),
                            size=graphene.Int())

    ids = graphene.List(DictEntry, dict_id=graphene.String(), lemma_id=graphene.List(graphene.String),
                        size=graphene.Int())

    def resolve_entries(self, info, dict_id, query, query_type, field, size):
        res = get_from_elastic(dict_id=dict_id, query=query, size=size, query_type=query_type, field=field)
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))

    def resolve_ids(self, info, dict_id, lemma_id, size):
        res = get_from_elastic(dict_id=dict_id, query=lemma_id, size=size, query_type='ids')
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))
