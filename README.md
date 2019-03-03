# Kosh - APIs for Dictionaries

## How to run Kosh (Linux, OSX) with data from [kosh_data](https://github.com/cceh/kosh_data):

1. [elasticsearch](https://www.elastic.co/downloads/elasticsearch)  must be running on your computer
2. `git clone https://github.com/cceh/kosh`
3. `git clone https://github.com/cceh/kosh_data`
4. `cd kosh`
5. `make`
5. start kosh:

    on Linux: 
     
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost`
    
    on OSX:
     
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost --data_sync off`

## Query samples:

### Hönig (Kölsch-Deutsch)

* REST: <http://kosh.uni-koeln.de/api/hoenig/restful/entries?query=scha&query_type=prefix&field=lemma_ksh>

* GraphQL: <http://kosh.uni-koeln.de/api/hoenig/graphql>
```
{
  entries(queryType: prefix, query: "scha", field:lemma_ksh ) {
    id 
    lemmaKsh
    translationDeu
  }
}
```

### TuniCo - [A Dictionary of Tunis Arabic](https://arche.acdh.oeaw.ac.at/browser/oeaw_detail/id.acdh.oeaw.ac.at/uuid/175b8cdf-5d04-f4d3-a778-67910aa8fd37)


* REST: <http://kosh.uni-koeln.de/api/tunico/restful/entries?query=.*ung&query_type=regexp&field=trans_de>

* GraphQL: <http://kosh.uni-koeln.de/api/tunico/graphql>

```
{
  entries(queryType: regexp, query: ".*ung", field: trans_de) {
    id 
    lemma	 
    transEn
    transDe
  }
}
```

### [Freedict German - Dutch](https://github.com/freedict/fd-dictionaries/tree/master/deu-nld)

* REST: <http://kosh.uni-koeln.de/api/freedict_deu_nld/restful/entries?query=lieben&query_type=term&field=lemma_deu>

* GraphQL:  <http://kosh.uni-koeln.de/api/freedict_deu_nld/graphql>
```
{
  entries(queryType: term, query: "lieben", field: lemma_deu) {
    id 
    translationNld
  }
}
```


### [Hiztegi Batu Oinarriduna](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.xml) (Basque)

* REST: <http://kosh.uni-koeln.de/api/hiztegibatua/restful/entries?query=*etsu&query_type=wildcard&field=lemma>

* GraphQL:  <http://kosh.uni-koeln.de/api/hiztegibatua/graphql>
```
{
  entries(queryType: wildcard, query: "*etsu", field: lemma) {
    id 
    lemma
    sensePos
    xml
  }
}
```