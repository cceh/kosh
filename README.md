# Kosh - APIs for Dictionaries

The following examples are based on data modules found in the repository [kosh_data](http://github/cceh/kosh_data)

## API Interaction:

Kosh offers instances of Swagger UI and  GraphiQL per indexed dataset.

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

### [English Wordnet](https://en-word.net/)

Entries Index:

* Swagger UI: <http://kosh.uni-koeln.de/api/wordnet_en_entry/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/wordnet_en_entry/graphql>

Synsets Index:

* Swagger UI: <http://kosh.uni-koeln.de/api/wordnet_en_synset/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/wordnet_en_synset/graphql>

