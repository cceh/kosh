---
layout: default
title: API Access and Search
nav_order: 3
---

# API Access and Search
{: .no_toc}

1. TOC
{:toc}




## API Access

Both APIs, REST and GraphQL, provide access to the same data that is contained in an elasticsearch index.
You can access each REST API via Swagger and each GraphQL API via GraphiQL.

### REST

Kosh creates for each data module, two endpoints: `entries` and `ids`.

Each REST API comes with a Swagger UI. This is the best way to grasp the potential your API.

After deploying, you can search on each data module at the following address:

REST (Swagger UI): `http://localhost:5000/[your_index_name_here]/api/restful`


### GraphQL

Graphql offers only one endpoint but two query types: `entries` and `ids`.

GraphiQL: `http://localhost:5000/[your_index_name_here]/api/graphql`

## Search

The most important functionality of a digital dictionary is to provide an efficient search system.
Therefore at the core of the Kosh system is elasticsearch, an open-source search engine that is fast and design to scale with little effort.

### Overview

- In both APIs of each dataset, you can do the same type of queries. The difference between both APIs is that in GraphQL you have to specify which fields should be returned.
- Besides the fields that you have configured to be indexed, Kosh indexes per default the whole XML entry. The XML tags and attributes are not indexed. 
This means that you can search in the whole text of the entry. This comes handy when the datset has not been properly structured and you need to search on it while working on its improvement.


### Query types

Kosh offers the following elastic subset query types:
```
term 
match
fuzzy 
wildcard 
regexp 
prefix 
terms 
match_phrase 
```

### Query example

#### REST API

In the Basque dictionary '[Hiztegi Batua](/implementations/kosh_data.md#hiztegi-batua-basque)' get those the entries with headwords ending with 'eko':

A REST version of this query would look like this:

<https://kosh.uni-koeln.de/api/hiztegibatua/restful/entries?field=lemma&query=*eko&query_type=wildcard>

Elasticsearch returns per default a maximum of 20 results per query. You can increase this value with the `size` parameter:

<https://kosh.uni-koeln.de/api/hiztegibatua/restful/entries?field=lemma&query=*eko&query_type=wildcard&size=50>


#### GraphQL API

In GraphQL you have to declare explicitly which fields you would like to receive in the results.
Let's only ask for those lemmas ending with 'eko':

```graphql
{
  entries(queryType: wildcard, query: "*eko", field: lemma, size: 50) {
    lemma
  }
}

```

Copy + paste the query snippet and execute it here: <https://kosh.uni-koeln.de/api/hiztegibatua/graphql>
