class query():
  pass

# #
# #
# # REST
# #
# #
# def get_from_elastic(dict_id, query, query_type=None, field=None):
#     if query_type == 'ids':
#         res = client.search(index=dict_id,
#                             body={
#                                 "query": {'ids': {'values': query}},
#                                 "sort": [
#                                     {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                 ]})
#     else:
#         if query_type == 'fuzzy':
#             res = client.search(index=dict_id,
#                                 body={
#                                     "query": {"fuzzy": {field: {"value": query,
#                                                                 "prefix_length": 1,
#                                                                 "fuzziness": 1}}},
#                                     "sort": [
#                                         {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                     ]
#                                 })
#         else:
#             res = client.search(index=dict_id,
#                                 body={
#                                     "query": {query_type: {field: query}},
#                                     "sort": [
#                                         {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                     ]})
#     return res


# def select_from_elatic_response(elastic_raw):
#     data = {}
#     from_elastic = []
#     for e in elastic_raw:
#         elastic_result = {}
#         elastic_result['id'] = e['_id']
#         elastic_result['headword_iso'] = e['_source']['headword_iso']
#         elastic_result['headword_slp1'] = e['_source']['headword_slp1']
#         elastic_result['headword_hk'] = e['_source']['headword_hk']
#         elastic_result['headword_deva'] = e['_source']['headword_deva']
#         elastic_result['headword_ascii'] = e['_source']['headword_ascii']
#         elastic_result['entry_tei_iso'] = e['_source']['entry_tei_iso']
#         from_elastic.append(elastic_result)
#     data['data'] = from_elastic
#     return data


# #
# #
# # GRAPHQL
# #
# #
# def get_from_elastic(dict_id, query, size=None, query_type=None, field=None):
#     # set max size auf 100:
#     if size is not None and size > 100:
#         size = 100

#     if query_type == 'ids':
#         res = client.search(index=dict_id,
#                             body={
#                                 "query": {'ids': {'values': query}},
#                                 "sort": [
#                                     {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                 ],
#                                 "from": 0, "size": size})
#     else:
#         if query_type == 'fuzzy':
#             res = client.search(index=dict_id,
#                                 body={
#                                     "query": {"fuzzy": {field: {"value": query,
#                                                                 "prefix_length": 1,
#                                                                 "fuzziness": 1}}},
#                                     "sort": [
#                                         {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                     ]
#                                     ,
#                                     "from": 0, "size": size
#                                 })
#         else:
#             res = client.search(index=dict_id,
#                                 body={
#                                     "query": {query_type: {field: query}},
#                                     "sort": [
#                                         {"sort_id": {"order": "asc", "unmapped_type": "integer", "mode": "avg"}}
#                                     ],
#                                     "from": 0, "size": size})
#     return res

# def select_from_elastic_response(elastic_raw):
#     from_elastic = []
#     for e in elastic_raw:
#         elastic_result = {}
#         elastic_result['id'] = e['_id']
#         elastic_result['sort_id'] = e['_source']['sort_id']
#         elastic_result['headword_iso'] = e['_source']['headword_iso']
#         elastic_result['headword_slp1'] = e['_source']['headword_slp1']
#         elastic_result['headword_hk'] = e['_source']['headword_hk']
#         elastic_result['headword_deva'] = e['_source']['headword_deva']
#         elastic_result['headword_ascii'] = e['_source']['headword_ascii']
#         entry_tei_iso = e['_source']['entry_tei_iso']
#         elastic_result['entry_tei_iso'] = entry_tei_iso
#         elastic_result['sense_txt_iso'] = extract_sense(entry_tei_iso)
#         elastic_result['sense_html_iso'] = sense_as_html(entry_tei_iso)
#         from_elastic.append(elastic_result)
#     return from_elastic





# ####################
# # Schema for entries in elastic


# parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

# style = '''
# <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
#   xmlns:ns="http://www.tei-c.org/ns/1.0" version="1.0"
#   exclude-result-prefixes="ns">

#  <xsl:output method="html"/>

#   <xsl:template match="ns:entry">
#     <div>
#     <xsl:apply-templates select="ns:sense"/>
#     </div>
#    </xsl:template>

#    <xsl:template match="ns:sense">
#    <xsl:apply-templates/>
#    </xsl:template>

#    <xsl:template match="ns:hi[@rendition='#b']">
#    <b>
#       <xsl:apply-templates/>
#     </b>
#    </xsl:template>

#    <xsl:template match="ns:hi[@rendition='#i']">
#    <i>
#       <xsl:apply-templates/>
#     </i>
#    </xsl:template>


#    <xsl:template match="ns:hi[@rendition='#wide']">
#    <i>
#       <xsl:apply-templates/>
#     </i>
#    </xsl:template>

#    <xsl:template match="ns:w[@xml:lang='el']">
#     <i>
#       <xsl:apply-templates/>
#     </i>
#    </xsl:template>

#    <xsl:template match="ns:w[@xml:lang='he']">
#     <i>
#       <xsl:apply-templates/>
#     </i>
#    </xsl:template>

#    <xsl:template match="ns:lb">
#       <br/>
#    </xsl:template>

# </xsl:stylesheet>
# '''


# def sense_as_html(entry_tei):
#     tree = etree.parse(StringIO(entry_tei), parser)
#     entry = tree.xpath('.')[0]
#     xslt_root = etree.XML(style, parser)
#     transform = etree.XSLT(xslt_root)
#     result_tree = transform(entry)
#     result_tree = str(result_tree)
#     result_tree = result_tree.replace('\n', '')
#     return result_tree


# def extract_sense(entry_tei):
#     tree = etree.parse(StringIO(entry_tei), parser)
#     entry = tree.xpath('.')[0]
#     entry_sense = entry.xpath('./ns:sense', namespaces=namespaces)[0]
#     entry_sense = etree.tostring(entry_sense, encoding='unicode', pretty_print=True)
#     soup = BeautifulSoup(entry_sense, 'lxml')
#     entry_sense = soup.get_text()
#     # remove \n
#     entry_sense = entry_sense.replace('\n', '')
#     return entry_sense
