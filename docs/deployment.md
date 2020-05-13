---
layout: default
title: Deployment
nav_order: 2
---

# Deploying Kosh 
{: .no_toc}

1. TOC
{:toc}

## Input: Data module

A Kosh data module consists of: 
1.  [Lexical data in XML](#data_xml)
2.  [Config file in JSON](#config_json)
3. ['.kosh' file](#kosh_file)

### <a name="data_xml"></a>Lexical data in XML 
You can add to Kosh **any valid XML** file. The following entry belongs to the the Basque dictionary Hiztegi Batua.
This dictionary has been compiled by the Academy of the Basque Language, Euzkaltzaindia. It is available in 
[PDF](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.pdf) and in [XML](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.xml) format. 
You can also access it at [Kosh Data](implementations/kosh_data.md)

```xml
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

### <a name="config_json"></a>Config file

In a JSON file, information about the XML nodes to be indexed and their subnodes are to be specified in XPath 1.0 notation.
Elasticsearch indexes arrays of elements natively. In order to inform Kosh and thus elasticsearch if this is the case, 
in the property "fields", you must add square braquets to the respective value, e.g. "[sense_def]".

 
If you want to save the strings 'as they are', i.e. without preprocessing, use `"type":"keyword"`.

If you want to preprocess strings (analyze them before indexing), i.e. let them be analyze by elasticsearch, use `"type":"text"`.

If your dictionary does not have IDs for the entries, Kosh creates them automatically.

Per default the whole entry is indexed. In this process the XML tags are not analyzed, i.e. you can not search for them.  


```json
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


### <a name="kosh_file"></a>'.kosh' file

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

If your dictionary is split into multiple files, this is not a problem:


```
[de_alcedo]
files: ["alcedo-1.tei", "alcedo-2.tei", "alcedo-3.tei", "alcedo-4.tei", "alcedo-5.tei"]
schema: de_alcedo_mapping.json
```

## Running Kosh

Kosh can be deployed natively on Unix-like systems or with Docker. 

If you deploy it natively on Linux systems, data synchronization is guaranteed, i.e. if you modify any file of a data module, Kosh will update the index. 
This feature is not available for macOS.

### Natively on Unix-like Systems

Requirements:

python 3+

[elasticsearch 7+]

Procedure:

1. Clone the repository
```bash
$ git clone https://github.com/cceh/kosh
```
2. Go to the repository
```bash
$ cd kosh
```
3. Build
```bash
make
```

4. Run

    on Linux: 
    ```bash
    $ kosh --log_level DEBUG --data_root [path_to_your_data_dir] --data_host localhost
    ```
   on OSX:  
   ```bash
    $ kosh --log_level DEBUG --data_root [path_to_your_data_dir] --data_host localhost --data_sync off
    ```

### With Docker

Procedure:

1.  `git clone https://github.com/cceh/kosh
`

2.  `cd kosh`

3.  In `docker-compose.override.yml`, you need to specify the path to your data modules, i.e. replace`../kosh_data/hoenig`:    
   
``` dockerfile
    
version: '2.3'

services:
  elastic:
    ## Uncomment the next line when the host network should be used.
    # network_mode: host

    ## Uncomment the next line when deploying in production.
    # restart: always

  kosh:
    ## Uncomment the next line when the host network should be used.
    # network_mode: host

    ## uncomment the next line when deploying in production
    # restart: always

    ## volumes:
    ##   - PATH_TO_KOSH_INI_FILE:/etc/kosh.ini:ro
    ##   - PATH_TO_XML_LEXICAL_DATA_WITH_KOSH_FILES:/var/lib/kosh:ro
    volumes:
      - ./kosh.ini:/etc/kosh.ini:ro
      - ../kosh_data/hoenig:/var/lib/kosh:ro

    command: ['--config_file', '/etc/kosh.ini']
```


4. `sudo docker-compose up -d`


To check the logs:

`sudo docker-compose logs`

To stop and redeploy:

`sudo docker-compose down`

## Sample datasets: [Kosh Data](/implementations/kosh_data.md)

In [Kosh Data](/implementations/kosh_data.md) you can find datasets to be deployed with Kosh. 
For each of them you will find the required files by Kosh: lexical data encoded in XML, a JSON config file and a '.kosh' file.
You can have a look at them to configure your own Kosh data modules. 
  