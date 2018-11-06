import pprint
from index_grassmann import GraEntry
from elasticsearch_dsl import Search, Q, connections
from unidecode import unidecode
from elasticsearch import Elasticsearch
import json
import requests

connections.create_connection(hosts=['localhost'])
client = Elasticsearch()


def test_query_id(id):
    entry = GraEntry.get(id=id)
    print(entry.sort_id)
    print(entry.headword_slp1)
    print(entry.headword_iso)
    print(entry.headword_gra)
    print(entry.entry_gra)


def test_query_entry(query, query_type):
    s = Search(using=client, index='gra')
    q = Q(query_type, entry_iso=query)
    s = s.query(q)
    # response = s.execute()
    print(s.count())
    print(s.to_dict())
    for hit in s:
        print(hit.meta.id)
        print(hit.entry_gra)


def test_query_headword(query_type, query, gra=False):
    s = Search(using=client, index='gra')
    if gra:
        q = Q(query_type, headword_gra=query)
    else:
        q = Q(query_type, headword_ascii=query)

    if s.count() == 0 and query_type == 'term':
        print('now fuzzy')
        if gra:
            q = Q('fuzzy', headword_gra=query)
        else:
            q = Q('fuzzy', headword_ascii=query)

    s = s.query(q)
    response = s.execute()
    print('query', q)

    print('results for this query: ', s.count())
    if s.count() > 0:
        print('took', response.took)
    print('total', response.hits.total)
    as_dict = response.to_dict()
    pprint.pprint(as_dict)


def test_query_gra(query_type, query, gra=False):
    s = Search(using=client, index='gra')
    if gra:
        q = Q(query_type, headword_gra=query)
    else:
        head_query = unidecode(query)
        q = Q(query_type, headword_ascii=head_query)

    if s.count() == 0 and query_type == 'term':
        s = Search(using=client, index='gra')

        if gra:
            print('now in searching in entry_gra')
            q = Q('match', entry_gra=query)
        else:
            print('now in searching in entry_iso')
            q = Q('match', entry_iso=query)

    s = s.query(q)
    response = s.execute()
    if s.count() > 0:
        print('took', response.took)
    print('total', response.hits.total)
    as_dict = response.to_dict()
    pprint.pprint(as_dict)


def test_query(query_type, query_string, meaning, query_entry=False):
    if len(query_string) > 9:
        query_string = query_string[:9]
    print(query_string)
    s = Search(using=client, index='gra')
    head_query = unidecode(query_string)
    if query_entry:
        q = Q(query_type, headword_ascii=head_query)

    else:
        q = Q('bool', must=[Q('fuzzy', headword_ascii=head_query)],
              should=[Q('match', entry_iso=meaning)])

    print('query', q)
    s = s.query(q)
    response = s.execute()
    print(s.count())
    if s.count() > 0:
        print('took', response.took)
    print('total', response.hits.total)
    as_dict = response.to_dict()
    pprint.pprint(as_dict)


def very_simple_search(clean_string, hom):
    res = client.search(index="gra",
                        body={
                            "query": {
                                "bool": {
                                    "must":
                                        {
                                            "term": {"headword_ascii": clean_string}
                                        }

                                    ,
                                    "filter": {
                                        "term": {"hom_number": hom}
                                    }
                                }}})
    return res


def calculate_fuzz_value(string_to_query):
    if len(string_to_query) <= 2:
        fuzz_value = 1
    if len(string_to_query) > 2 and len(string_to_query) <= 5:
        fuzz_value = 2
    if len(string_to_query) > 5:
        fuzz_value = 3
    return fuzz_value


def go_fuzzy(string_to_query, pref_length=None, hom_value=None, meaning=None, simple_query=False, hom=False,
             filter_meaning=False):
    fuzz_value = calculate_fuzz_value(string_to_query)
    if simple_query:
        res = client.search(index="gra",
                            body={
                                "query": {"fuzzy": {"headword_ascii": {"value": string_to_query,
                                                                       "prefix_length": pref_length,
                                                                       "fuzziness": fuzz_value}}}})
        if res['hits']['total'] == 0:
            ##if the string has more than 7 chars, we only query the first 6
            if len(string_to_query) > 7:
                string_to_query = string_to_query[:6]
                print(string_to_query)
                res = client.search(index="gra",
                                    body={
                                        "query": {"fuzzy": {"headword_ascii": {"value": string_to_query,
                                                                               "prefix_length": pref_length,
                                                                               "fuzziness": fuzz_value}}}})
    if hom:
        res = client.search(index="gra",
                            body={
                                "query": {
                                    "bool": {
                                        "must":
                                            {
                                                "fuzzy": {
                                                    "headword_ascii":
                                                        {"value": string_to_query,
                                                         "prefix_length": pref_length,
                                                         "fuzziness": fuzz_value}
                                                }
                                            }
                                        ,
                                        "filter": {
                                            "term": {"hom_number": hom_value}
                                        }
                                    }}})
        if res['hits']['total'] == 0:
            ##if the string has more than 7 chars, we only query the first 6
            if len(string_to_query) > 7:
                string_to_query = string_to_query[:6]
                res = client.search(index="gra",
                                    body={
                                        "query": {
                                            "bool": {
                                                "must":
                                                    {
                                                        "fuzzy": {
                                                            "headword_ascii":
                                                                {"value": string_to_query,
                                                                 "prefix_length": pref_length,
                                                                 "fuzziness": fuzz_value}
                                                        }
                                                    }
                                                ,
                                                "filter": {
                                                    "term": {"hom_number": hom_value}
                                                }
                                            }}})

    if filter_meaning:
        res = client.search(index="gra",
                            body={
                                "query": {
                                    "bool": {
                                        "must":
                                            {
                                                "fuzzy": {
                                                    "headword_ascii":
                                                        {"value": string_to_query,
                                                         "prefix_length": pref_length,
                                                         "fuzziness": fuzz_value}
                                                }
                                            }
                                        ,
                                        "filter": {
                                            "match": {"entry_iso": meaning}
                                        }
                                    }}})
        if res['hits']['total'] == 0:
            ##if the string has more than 7 chars, we only query the first 6
            if len(string_to_query) > 7:
                string_to_query = string_to_query[:6]
                res = client.search(index="gra",
                                    body={
                                        "query": {
                                            "bool": {
                                                "must":
                                                    {
                                                        "fuzzy": {
                                                            "headword_ascii":
                                                                {"value": string_to_query,
                                                                 "prefix_length": pref_length,
                                                                 "fuzziness": fuzz_value}
                                                        }
                                                    }
                                                ,
                                                "filter": {
                                                    "match": {"entry_iso": meaning}
                                                }
                                            }}})

    return res


# r = complex_search('sanu', 1, 2, simple=True)
#res = go_fuzzy(unidecode('hotar'), pref_length=1, simple_query=True)

#print(res)
test_query_id('lemma_id_1695')