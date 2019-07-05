# Kosh - APIs for Dictionaries

Kosh is an open-source software framework developed for creating and maintining APIs for dictionaries

## Overview


<img src="img/kosh_core_overview.png"/>


## Features



* Kosh processes as input lexical data in XML format.
* You configure which nodes must be indexed in elasticsearch.
* Two APIs, a GraphQL and a REST API access the data stored in elasticsearch.
* Kosh can be deployed either via Docker or natively on Unix-based systems.

## Deployment

### Input: Data module

A Kosh data module consists of: 
1.  [Lexical data in XML](#data_xml)
2.  [Config file in JSON](#config_json)
3. ['.kosh' file](#kosh_file)

##### <a name="data_xml"></a> 1. Lexical data in XML 
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

##### <a name="config_json"></a> 2. Config file

In a JSON file, information about the XML nodes to be indexed and their subnodes are to be specified in XPath 1.0 notation.
Elasticsearch indexes arrays of elements natively. In order to inform Kosh and thus elasticsearch if this is the case, 
in the property "fields", you must add square braquets to the respective value, e.g. "[sense_def]".

 
If you want to save the strings 'as they are', i.e. without preprocessing, use `"type":"keyword"`.

If you want to avoid saving strings with punctuation, i.e. let them be analyze by elasticsearch, use`"type":"text"`.

If your dictionary does not have IDs for the entries, Kosh creates them automatically.

Per default the whole entry is indexed. In this process the XML tags are not analyzed, i.e. you can not search for them.  


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
Configuration file ([hiztegibatua_mapping.json](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua_mapping.json)) for  
the [hiztegibatua](https://github.com/cceh/kosh_data/blob/master/hiztegibatua/hiztegibatua.xml) dictionary.


##### <a name="kosh_file"></a>3. '.kosh' file

You need create a '.kosh' file, on each data module for informing Kosh about:
+ The index name for your dataset
+ Where to find the XML data
+ Where to find the configuration file

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

Kosh can be deployed natively on Unix-systems or via Docker. 

If you deploy it natively on Linux systems, data synchronization is guaranteed, i.e. if you modify any file of a data module, Kosh will update the index. 
This feature is not available for macOS.

#### Natively on Unix-Systems

Requirements:

python 3+

[elasticsearch 7.0](https://www.elastic.co/downloads/past-releases/elasticsearch-7-0-0)

Procedure:

1. `git clone https://github.com/cceh/kosh
`

2. `cd kosh`

3. `make`

4. start kosh:

    on Linux: `kosh --log_level DEBUG --data_root [path_to_your_data_dir] --data_host localhost`

    on OSX: `kosh --log_level DEBUG --data_root [path_to_your_data_dir] --data_host localhost --data_sync off`


#### With Docker

Procedure:

1.  `git clone https://github.com/cceh/kosh
`

2.  `cd kosh`

3.  In `docker-compose.local.yml`, you need to specify the path to your data modules, i.e. replace`../kosh_data`:    
   
    ``` 
    version: '2.3'
        services:
        kosh:
        volumes: ['../kosh_data:/var/lib/kosh:ro']
    ```

4. `sudo docker build -t cceh/kosh .`
5. `sudo docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d`


To check the logs:

`sudo docker-compose logs`

To stop and later rebuild:

`sudo docker-compose down`

## Searching

### REST

Kosh creates per each data module, two endpoints: `entries` and `ids`.

Each REST API comes with a Swagger UI. This is the best way to grasp the potential your API.

After deploying, you can search on each data module at the following address:

REST (Swagger UI): `http://localhost:5000/[your_index_name_here]/api/rest`


### GraphQL

Graphql offers only one endpointm but two query types: `entries` and `ids`.

Feel free to test your API with GraphiQL: `http://localhost:5000/[your_index_name_here]/api/graphql`


## Contact 
If you have any questions, please contact the Kosh team: info-kosh[a]uni-koeln.de