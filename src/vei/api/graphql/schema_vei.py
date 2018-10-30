import json
from collections import namedtuple
from io import StringIO

import graphene
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from lxml import etree

client = Elasticsearch()
namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    print(data)
    return json.loads(data, object_hook=_json_object_hook)


####################
# Schema for entries in elastic


parser = etree.XMLParser(recover=True)


def extract_sense(entry_tei):
    tree = etree.parse(StringIO(entry_tei), parser)
    entry = tree.xpath('.')[0]
    vei_sense = entry.xpath('./ns:sense', namespaces=namespaces)[0]
    vei_sense = etree.tostring(vei_sense, encoding='unicode', pretty_print=True)
    soup = BeautifulSoup(vei_sense, 'lxml')
    vei_sense = soup.get_text()
    # remove \n
    vei_sense = vei_sense.replace('\n', '')
    return vei_sense


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
        from_elastic.append(elastic_result)
    return from_elastic


class VEIEntry(graphene.ObjectType):
    id = graphene.String()
    sort_id = graphene.Int()
    headword_iso = graphene.String()
    headword_slp1 = graphene.String()
    headword_hk = graphene.String()
    headword_deva = graphene.String()
    headword_ascii = graphene.String()
    entry_tei_iso = graphene.String()
    sense_txt_iso = graphene.String()


# queries

def get_from_elastic(query, size=None, query_type=None, field=None):
    # set max size auf 100:
    if size is not None and size > 100:
        size = 100

    if query_type == 'ids':
        res = client.search(index="vei",
                            body={
                                "query": {'ids': {'values': query}},
                                "sort": [
                                    {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                ],
                                "from": 0, "size": size})
    else:
        if query_type == 'fuzzy':
            res = client.search(index="vei",
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
            res = client.search(index="vei",
                                body={
                                    "query": {query_type: {field: query}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ],
                                    "from": 0, "size": size})
    return res


class VEIQuery(graphene.ObjectType):
    entries = graphene.List(VEIEntry, query=graphene.String(), query_type=graphene.String(),
                            field=graphene.String(),
                            size=graphene.Int())

    ids = graphene.List(VEIEntry, lemma_id=graphene.List(graphene.String), size=graphene.Int())

    def resolve_entries(self, info, query, query_type, field, size):
        res = get_from_elastic(query, size=size, query_type=query_type, field=field)
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))

    def resolve_ids(self, info, lemma_id, size):
        res = get_from_elastic(query=lemma_id, size=size, query_type='ids')
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))
