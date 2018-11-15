import requests


def test_entry_request(dict_id, query, query_type):
    r = requests.get('http://localhost:5000/dicts/sa/rest/v1/search/' + dict_id,
                     params={'entry': query, 'query_type': query_type})
    print(r.url)
    return r


def test_standard_search(dict_id, query, query_type, input_translit):
    r = requests.get('http://localhost:5000/dicts/sa/rest/v1/search/' + dict_id,
                     params={'headword': query, 'query_type': query_type, 'input_translit': input_translit})
    print(r.url)
    return r


def test_headword_id(dict_id, _id):
    r = requests.get('http://localhost:5000/dicts/sa/rest/v1/headwords/' + dict_id + '/' + _id)
    print(r.url)
    return r


def test_headword_id_context(dict_id, _id, limit):
    r = requests.get('http://localhost:5000/dicts/sa/rest/v1/headwords/' + dict_id + '/' + _id + '/context',
                     params={'limit': limit})
    print(r.url)
    return r


# print(test_headword_request('gat', 'prefix').json())

print(test_headword_id_context(dict_id='bhs', _id='4', limit=50))
# agni
# print(test_headword_request('agn.*','regexp'))
# print(test_headword_request('अक्ष', 'prefix', 'deva'))
# print(test_standard_search('ap90', 'agni', 'prefix', 'iso'))
# print(test_headword_id('ap90', '78'))
