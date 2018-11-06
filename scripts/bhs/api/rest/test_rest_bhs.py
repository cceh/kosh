import requests


def test_entry_request(query, query_type):
    r = requests.get('http://localhost:5002/dicts/bhs/rest/v1/search',
                     params={'entry': query, 'query_type': query_type})
    print(r.url)
    return r


def test_standard_search(query, query_type, input_translit):
    r = requests.get('http://localhost:5002/dicts/bhs/rest/v1/search',
                     params={'headword': query, 'query_type': query_type, 'input_translit': input_translit})
    print(r.url)
    return r


def test_headword_id(id):
    r = requests.get('http://localhost:5002/dicts/bhs/rest/v1/headwords/',
                     params={'id': id})
    print(r.url)
    return r


def test_headword_id_context(id, limit):
    r = requests.get('http://localhost:5002/dicts/bhs/rest/v1/headwords/' + id + '/context', params={'limit': limit})
    print(r.url)
    return r


# print(test_headword_request('gat', 'prefix').json())

print(test_headword_id_context(id='30', limit=40))
# agni
# print(test_headword_request('agn.*','regexp'))
# print(test_headword_request('अक्ष', 'prefix', 'deva'))
#print(test_standard_search('agn', 'prefix', 'iso'))
# print(test_headword_id(78))
