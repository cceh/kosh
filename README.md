# kosh - APIs for Dictionaries


## ElasticSearch and XPath JSON Schema example
```
{
  "mappings": {
    "entry": {
      "_meta": {
        "_xpaths": {
          "id": ".tei:[@xml:id]",
          "root": "//tei:entry",
          "fields": {
            "lemma": "./tei:form[@type='lemma']/orth",
            "variants": ".//tei:form[@type='variant']/orth"
          }
        }
      },
      "properties": {
        "lemma": {
          "type": "keyword"
        },
        "variants": {
          "type": "keyword"
        }
      }
    },
    "example": {
      "_meta": {
        "_xpaths": {
          "id": "./tei:[@xml:id']",
          "root": "//tei:cit[@type='example']",
          "fields": {
            "example_ar": "./tei:quote",
            "example_xml": "."
          }
        }
      },
      "properties": {
        "example_ar": {
          "type": "keyword"
        },
        "example_xml": {
          "type": "text"
        }
      }
    }
  }
}
```
