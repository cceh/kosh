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

When you run Kosh, your data is first parsed and indexed by [Elasticsearch](https://www.elastic.co/elasticsearch/). After your data has been processed, two APIs (both REST and GraphQL) are deployed which provide access to it.

You can inspect the API endpoints through [Swagger](https://swagger.io/) for the REST API and [GraphiQL](https://github.com/graphql/graphiql/blob/main/packages/graphiql/README.md) for the GraphQL API.

<!-- TODO: Add section with general info available through /api/id/ -->

### REST

For each data module, Kosh creates two endpoints: `entries` and `ids`.

`entries` lets you query items based on a search string. It returns all items (and their properties) that match your query. You will find an in-depth look at how [search](#search) works below.

`ids` returns the items matching the requested IDs.

After deploying Kosh locally, you can access each data module's contents at the following address, swapping `[your_index_name_here]` for the real index name of that module:

`http://localhost:5000/api/[your_index_name_here]/restful`

That link will also lead you to the Swagger UI where you can experiment with queries and check which parameters are required. Data is served as JSON.

### GraphQL

GraphQL offers only one endpoint but two query fields: `entries` and `ids`.

As described above, they provide you with the means to either search items based on an arbitrary search string or to pull out specific items based on their ID.

After deploying Kosh locally, you can access each data module through GraphQL by using the following endpoint:

`http://localhost:5000/api/[your_index_name_here]/graphql`

There, you can also use the GraphiQL "playground" to experiment with queries, with the added benefit of error highlighting and auto-completion.

## Search

The most important functionality of a digital dictionary is to provide an efficient search system. Therefore, at the core of the Kosh system is Elasticsearch, an open-source search engine that is fast and designed to scale with little effort.

### Overview

Regardless of the API you are using, the basic structure of your search query and the data you get in return are the same. The difference between both APIs is that in GraphQL, you have to specify which fields should be returned.

Besides the fields that you have explicitly configured to be indexed, Kosh indexes, per default, the whole XML entry. XML tags and attributes are **not** indexed.

This approach enables you to use full-text search across the entire content of the entry, which also comes in handy when the structure of the data has not yet been finalized, but you already want to search through it while working to improve it.

### Query Structure

Querying for `entries`, the search string is matched against the content of a specific field or property of each lexical item. There are several search strategies which may be used that we call query types ([see below](#query-types) for a full list).

Required fields: 
* the field you want to query (`field`), 
* your query string (`query`), 
* the query type (`query_type`)

Optional fields are: 
* the number of entries you want returned (`size`, the default is 20)

### Query Types

Kosh offers the following subset of Elasticsearch query types:

| Query Type | Explanation |
|---|---|
| `term` | Returns documents that contain an exact term in a provided field. |
| `match` | Returns documents that match a provided text, number, date or boolean value. |
| `fuzzy` | Returns documents that contain terms similar to the search term. Similarity, or fuzziness, is measured using a Levenshtein edit distance. |
| `wildcard` | Returns documents that contain terms matching a wildcard pattern. |
| `regexp` | Returns documents that contain terms matching a regular expression. |
| `prefix` | Returns documents that contain a specific prefix in a provided field. |
| `terms` | Returns documents that contain one or more exact terms in a provided field. |
| `match_phrase` | Returns documents that contain an exact phrase. |

From the Elasticsearch Documentation:
* [term-level queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/term-level-queries.html)
* [full-text queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html)

### Query Example

In this section, we want to look at a specific example of how to query data using both the REST and GraphQL API endpoints.

Say you want to query the Basque dictionary [Hiztegi Batua](/implementations/kosh_data.md#hiztegi-batua-basque), which we provide as part of the Kosh sample data. 
If you want to get all the entries in that dictionary with lemmas ending in `eko`, you could use the following queries.

#### REST API

A REST version of the query would look like this:

<https://kosh.uni-koeln.de/api/hiztegibatua/restful/entries?field=lemma&query=*eko&query_type=wildcard>

The parameters used:
```
field = lemma
query = *eko
query_type = wildcard
```

#### GraphQL API

While REST returns the entire dictionary entry, GraphQL only supplies what you explicitly ask for. 
To return only the lemmas:

```graphql
{
  entries(queryType: wildcard, query: "*eko", field: lemma) {
    lemma
  }
}
```

For testing, copy & paste the query snippet and execute it here: <https://kosh.uni-koeln.de/api/hiztegibatua/graphql>
