# Kosh - APIs for Dictionaries

Kosh is an open-source software framework developed for creating and maintining APIs for dictionaries

## Overview


<img src="drawing.jpg" alt="img/kosh_core_overview.png" width="200"/>


* Kosh processes as input lexical data in XML format.
* In a JSON config file info about the fields to be indexed and their datatype must be provided
* Two APIs, a GraphQL and a REST API access the data stored in elasticsearch.
* Kosh can be deployed either via Docker or natively on Unix-based systems.

## Deployment

### ok

A data module for Kosh consists of: 
1.  [Lexical data in XML](#data_xml)
2.  [Config file in JSON](#config_json)
3. ['.kosh' file](#kosh_file)

#### <a name="data_xml"></a> 1. Lexical data in XML 
You can index any kind of **valid** XML files. The following entry belongs to the dictionary [hiztegibatua](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua.xml) :

```
 <entry id="13">
    <form>
      <orth>abadetasun</orth>
    </form>
    <sense n="1">
      <gramGrp>
        <pos>
          <q>iz.</q>
        </pos>
      </gramGrp>
      <def>monasterioko buruaren kargua eta egitekoa</def>
    </sense>
    <sense n="2">
      <gramGrp>
        <pos>
          <q>iz.</q>
        </pos>
      </gramGrp>
      <def>apaizgoa</def>
      <usg type="geo">
        <q>Bizk.</q>
      </usg>
    </sense>
  </entry>
``` 

#### <a name="config_json"></a> 2. Config file

In a JSON file, information about the XML nodes to be indexed and their subnodes are to be specified in XPATH 1.0 notation.
Elasticsearch indexes arrays of elements natively. In order to inform Kosh and thus elasticsearch if this is the case, 
in the property "fields", you must add square braquets to the respective value, e.g. "[sense_def]". 
This is a configuration file ([hiztegibatua_mapping.json](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua_mapping.json)) for  
the [hiztegibatua](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua.xml) dictionary.

```
{
  "mappings": {
    "_meta": {
      "_xpaths": {
        "id": "./@id",
        "root": "//entry",
        "fields": {
          "lemma": "./form/orth",
          "[sense_def]": "./sense/def",
          "[sense_pos]": "./sense/gramGrp/pos/q",
          "[dicteg]": "./sense/dicteg/q"
        }
      }
    },
    "properties": {
      "lemma": {
        "type": "keyword"
      },
      "sense_def": {
        "type": "text"
      },
      "sense_pos": {
        "type": "text"
      },
      "dicteg": {
        "type": "text"
      }
    }
  }
}

```

#### <a name="kosh_file"></a>3. '.kosh' file

In order to inform kosh about i) the index name for your dataset, ii) where to find the XML data, 
and iii) where to find the configuration file, you need create a '.kosh' file, providing this information.
The following is the '.kosh' file for [hiztegibatua](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua.xml)

```
[hiztegibatua]
files: ["hiztegibatua.xml"]
schema: hiztegibatua_mapping.json
```

If your dictionary is split into multiple files, you can only need to separate them between commas:


```
[de_alcedo]
files: ["alcedo-1.tei", "alcedo-2.tei", "alcedo-3.tei", "alcedo-4.tei", "alcedo-5.tei"]
schema: de_alcedo_mapping.json
```

### Running Kosh

Kosh can be deployed natively on Unix-systems or via Docker. If you deploy it natively, 
we recommend to do it on Linux systems, because if you modify any file on a data module, e.g. update an XML file, 
then Kosh updates automatically the related index. This won't occur in Unix-based systems like macOS.
