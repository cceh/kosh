# Kosh - APIs for Dictionaries

## How to deploy Kosh (Linux, OSX) with data from [kosh_data](https://github.com/cceh/kosh_data):

Requirements:    
  * python 3
  * [elasticsearch](https://www.elastic.co/downloads/elasticsearch) 7.0
1. `git clone https://github.com/cceh/kosh`
2. `git clone https://github.com/cceh/kosh_data`
3. `cd kosh`
4. `make`
5. start kosh:

    on Linux: 
     
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost`
    
    on OSX:
     
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost --data_sync off`

## API Interaction:

Kosh offers instances of Swagger UI and  GraphiQL per indexed dataset.
For testing your local deployment, replace `http://kosh.uni-koeln.de/` with `http://localhost:5000/` in the following URLs.

### Wörterbuch der Kölner Mundart - Fritz Hönig (Kölsch-Deutsch)

* Swagger UI: <http://kosh.uni-koeln.de/api/hoenig/restful>

* GraphiQL: <http://kosh.uni-koeln.de/api/hoenig/graphql>
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


* Swagger UI: <http://kosh.uni-koeln.de/api/tunico/restful>

* GraphiQL: <http://kosh.uni-koeln.de/api/tunico/graphql>

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

* Swagger UI: <http://kosh.uni-koeln.de/api/freedict_deu_nld/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/freedict_deu_nld/graphql>
```
{
  entries(queryType: term, query: "lieben", field: lemma_deu) {
    id 
    translationNld
  }
}
```


### [Freedict Breton - French](https://github.com/freedict/fd-dictionaries/tree/master/bre-fra)

* Swagger UI: <http://kosh.uni-koeln.de/api/freedict_bre_fra/restful>

* GraphiQL:  <http://kosh.uni-koeln.de/api/freedict_bre_fra/graphql>
```
{
  entries(queryType: wildcard, query: "*eler", field: lemma_bre) {
    id 
    lemmaBre
    translationFra
  }
}
```

### [Hiztegi Batu Oinarriduna](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.xml) (Basque)

* Swagger UI: <http://kosh.uni-koeln.de/api/hiztegibatua/restful>

* GraphiQL:  <http://kosh.uni-koeln.de/api/hiztegibatua/graphql>
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



### Diccionario Geográfico-Histórico de las Indias Occidentales ó América (1786-1789) de Antonio de Alcedo

* Swagger UI: <http://kosh.uni-koeln.de/api/de_alcedo/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/de_alcedo/graphql>
```
{
  entries(queryType: wildcard, query: "*HUE", field: lemma) {
    id 
    lemma
    xml
  }
}
```
