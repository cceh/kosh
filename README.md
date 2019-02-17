# kosh - APIs for Dictionaries


## ElasticSearch and XPath JSON Schema example
```
{
  "settings": {
    "analysis": {
      "analyzer": {
        "markup_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "char_filter": [
            "html_strip"
          ],
          "filter": [
            "standard",
            "lowercase"
          ]
        }
      }
    }
  },
  "mappings": {
    "entry": {
      "_meta": {
        "_xpaths": {
          "id": "./@xml:id",
          "root": "//tei:entry",
          "fields": {
            "lemma": "./tei:form[@type='lemma']/tei:orth",
            "variant": "./tei:form[@type='variant']/tei:orth",
            "multiword": "./tei:form[@type='multiWordUnit']/tei:orth",
            "as_xml": "."
          }
        }
      },
      "properties": {
        "lemma": {
          "type": "keyword"
        },
        "multiword": {
          "type": "keyword"
        },
        "variant": {
          "type": "keyword"
        },
        "as_xml": {
          "type": "text"
        }
      }
    },
    "example": {
      "_meta": {
        "_xpaths": {
          "id": "./@xml:id",
          "root": "//tei:cit[@type='example']",
          "fields": {
            "example_text": "./tei:quote",
            "as_xml": "."
          }
        }
      },
      "properties": {
        "example_text": {
          "type": "keyword"
        },
        "as_xml": {
          "type": "text"
        }
      }
    }
  }
}
```
