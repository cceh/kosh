"""
``defaultconfig`` variable, containing the default configuration. Should be
passed to ``ConfigParser.read_dict`` to define sane default values.
"""

defaultconfig = {
    "DEFAULT": {
        "conf": "",
        "name": "kosh",
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "root": "/api",
    },
    "data": {
        "host": "127.0.0.1",
        "loop": 3,
        "pool": "%(name)s",
        "root": "/var/lib/%(name)s",
        "spec": ".%(name)s",
        "sync": 10,
        "wait": 60,
    },
    "info": {
        "desc": "%(name)s - APIs for Lexical Data",
        "link": "https://kosh.uni-koeln.de",
        "mail": "info-kosh@uni-koeln.de",
        "repo": "https://github.com/cceh/kosh",
    },
    "logger": {
        "level": "INFO",
        "file": "",
    },
    "namespaces": {
        "dc": "http://purl.org/dc/elements/1.1",
        "tei": "http://www.tei-c.org/ns/1.0",
    },
    "query_types": {
        "term": True,
        "fuzzy": True,
        "match": True,
        "match_phrase": True,
        "prefix": False,
        "wildcard": False,
        "regexp": False,
    },
}
