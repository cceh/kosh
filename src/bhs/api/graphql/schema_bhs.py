import graphene
import json
from collections import namedtuple
from elasticsearch import Elasticsearch
from lxml import etree
from io import StringIO
from bs4 import BeautifulSoup

client = Elasticsearch()


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
    gra_sense = entry.xpath('./sense')[0]
    gra_sense = etree.tostring(gra_sense, encoding='unicode', pretty_print=True)
    soup = BeautifulSoup(gra_sense, 'lxml')
    gra_sense = soup.get_text()
    # remove \n
    gra_sense = gra_sense.replace('\n', '')
    return gra_sense


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
        elastic_result['headword_gra'] = e['_source']['headword_gra']
        elastic_result['headword_ascii'] = e['_source']['headword_ascii']
        entry_tei_iso = e['_source']['entry_tei_iso']
        entry_tei_gra = e['_source']['entry_tei_gra']
        elastic_result['entry_tei_iso'] = entry_tei_iso
        elastic_result['entry_tei_gra'] = entry_tei_gra
        elastic_result['sense_txt_iso'] = extract_sense(entry_tei_iso)
        elastic_result['sense_txt_gra'] = extract_sense(entry_tei_gra)
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


# queries

def get_from_elastic(query, query_type=None, field=None):
    if query_type == 'ids':
        res = client.search(index="gra",
                            body={
                                "query": {'ids': {'values': query}},
                                "sort": [
                                    {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                ]})
    else:
        if query_type == 'fuzzy':
            res = client.search(index="gra",
                                body={
                                    "query": {"fuzzy": {field: {"value": query,
                                                                "prefix_length": 1,
                                                                "fuzziness": 1}}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ]
                                })
        else:
            res = client.search(index="gra",
                                body={
                                    "query": {query_type: {field: query}},
                                    "sort": [
                                        {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
                                    ]})
    return res


class GraQuery(graphene.ObjectType):
    entries = graphene.List(GraEntry, query=graphene.String(), query_type=graphene.String(),
                            field=graphene.String(),
                            limit=graphene.Int())

    ids = graphene.List(GraEntry, lemma_id=graphene.List(graphene.String))

    def resolve_entries(self, info, query, query_type, field):
        res = get_from_elastic(query, query_type, field)
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))

    def resolve_ids(self, info, lemma_id):
        res = get_from_elastic(query=lemma_id, query_type='ids')
        parsed_results = select_from_elastic_response(res['hits']['hits'])
        return json2obj(json.dumps(parsed_results))
