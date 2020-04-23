---
layout: default
title: Kosh Data
parent: Implementations
nav_order: 4
---


# Kosh Data

Kosh Data contains different datasets that can be downloaded from <a href="https://github.com/cceh/kosh_data">this repository</a>.
If you clone Kosh Data to your computer, you can deploy them locally with Kosh.

These are the datasets that you can access:

### Diccionario Geográfico-Histórico de las Indias Occidentales ó América (1786-1789) de Antonio de Alcedo

**19.010 Entries**

* Swagger UI: <http://kosh.uni-koeln.de/api/de_alcedo/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/de_alcedo/graphql>
```graphql
{
  entries(queryType: wildcard, query: "*hue", field: lemma) {
    id 
    lemma
    xml
  }
}
```

### [English Wordnet](https://en-word.net/)

Synsets Index:

**120.053 Synsets**

* Swagger UI: <http://kosh.uni-koeln.de/api/wordnet_en_synset/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/wordnet_en_synset/graphql>


Entries Index:

**163.079 Entries**

* Swagger UI: <http://kosh.uni-koeln.de/api/wordnet_en_entry/restful>
* GraphiQL:  <http://kosh.uni-koeln.de/api/wordnet_en_entry/graphql>



### [Glossarium mediæ et infimæ latinitatis](https://sourceforge.net/p/ducange/code/HEAD/tree/xml/) - Charles du Fresne, sieur du Cange

**89.975 Entries**

* Swagger: <https://kosh.uni-koeln.de/api/ducange/restful>

* GraphiQL: <https://kosh.uni-koeln.de/api/ducange/graphql>

```graphql
{
  entries(query: "*άϐα*", queryType: wildcard, field: foreign_grc) {
    lemma
    foreignGrc
  }
}

```



### Hiztegi Batua (Basque) [XML](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.xml), [PDF](http://www.euskaltzaindia.eus/dok/eaeb/hiztegibatua/hiztegibatua.pdf): 

**37.973 Entries**

* Swagger UI: <http://kosh.uni-koeln.de/api/hiztegibatua/restful>

* GraphiQL:  <http://kosh.uni-koeln.de/api/hiztegibatua/graphql>
```graphql
{
  entries(queryType: prefix, query: "aban", field: lemma) {
    id 
    lemma
    sensePos
    xml
  }
}
```


### TuniCo - [A Dictionary of Tunis Arabic](https://arche.acdh.oeaw.ac.at/browser/oeaw_detail/id.acdh.oeaw.ac.at/uuid/175b8cdf-5d04-f4d3-a778-67910aa8fd37)
**7.543 Entries**

* Swagger UI: <http://kosh.uni-koeln.de/api/tunico/restful>

* GraphiQL: <http://kosh.uni-koeln.de/api/tunico/graphql>

```graphql
{
  entries(queryType: regexp, query: ".*ung", field: trans_de) {
    id 
    lemma	 
    transEn
    transDe
  }
}
```

### Wörterbuch der Kölner Mundart - Fritz Hönig (Kölsch-Deutsch)
**10.780 Entries**
* Swagger UI: <http://kosh.uni-koeln.de/api/hoenig/restful>

* GraphiQL: <http://kosh.uni-koeln.de/api/hoenig/graphql>
```graphql
{
  entries(queryType: prefix, query: "scha", field:lemma_ksh ) {
    id 
    lemmaKsh
    translationDeu
  }
}
```
