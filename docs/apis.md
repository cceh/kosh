---
layout: default
title: APIs Access and Search
nav_order: 4
---

# API Access and Search
{: .no_toc}

1. TOC
{:toc}




## API Access

Both APIs, REST and GraphQL, provide access to the same data that is contained in an elasticsearch instance.
Each API provides a dedicated GUI for testing purposes. You can access each REST API via Swagger and each GraphQL API via GraphiQL.

### REST

Kosh creates for each data module, two endpoints: `entries` and `ids`.

Each REST API comes with a Swagger UI. This is the best way to grasp the potential your API.

After deploying, you can search on each data module at the following address:

REST (Swagger UI): `http://localhost:5000/[your_index_name_here]/api/restful`


### GraphQL

Graphql offers only one endpoint but two query types: `entries` and `ids`.

GraphiQL: `http://localhost:5000/[your_index_name_here]/api/graphql`

## Search

Kosh is a flexible 