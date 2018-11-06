import requests, json
from pprint import pprint


def test_simple_query():
    url = 'http://127.0.0.1:5001/gra/graphql'
    gql_query = {
        '{entries(queryType: "prefix", query: "Sru", field: "headword_slp1") {id headwordIso headwordGra}}'}
    print(gql_query)
    try:
        req = requests.get(url=url, params={'query': gql_query})
        print(req.url)
        # pprint(req.text)
    except requests.exceptions.ConnectionError as e:
        print(e)
    return req


req = test_simple_query()
pprint(req)
