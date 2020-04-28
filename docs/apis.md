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



