import re
import string
import unicodedata
from datetime import datetime
from unicodedata import normalize

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, Keyword, Text, Integer, Boolean, connections, analyzer, Index
from indic_transliteration import xsanscript
from indic_transliteration.xsanscript import SchemeMap, SCHEMES, HK, SLP1, DEVANAGARI, IAST
from lxml import etree
from unidecode import unidecode

# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])
client = Elasticsearch()

scheme_slp1_deva = SchemeMap(SCHEMES[SLP1], SCHEMES[DEVANAGARI])
scheme_slp1_hk = SchemeMap(SCHEMES[SLP1], SCHEMES[HK])
scheme_iast_slp1 = SchemeMap(SCHEMES[IAST], SCHEMES[SLP1])

namespaces = {'ns': 'http://www.tei-c.org/ns/1.0'}

html_strip = analyzer('html_strip',
                      tokenizer="standard",
                      filter=["standard", "lowercase"],
                      char_filter=["html_strip"])


class StandardEntry(DocType):
    # TODO: add page number
    sort_id = Integer()
    headword_slp1 = Keyword(fields={'raw': Keyword()})
    headword_iso = Keyword(fields={'raw': Keyword()})
    headword_hk = Keyword(fields={'raw': Keyword()})
    headword_deva = Keyword(fields={'raw': Keyword()})
    headword_ascii = Keyword(fields={'raw': Keyword()})

    # some entries have homographs, most of the time, they should be subetries
    hom = Boolean()
    hom_number = Integer()

    entry_tei_iso = Text(analyzer=html_strip)
    created = Date()

    def save(self, **kwargs):
        return super(StandardEntry, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.created


def create_index_man(es_client, index_name):
    # create ES client, create index
    if es_client.indices.exists(index_name):
        print("deleting '%s' index..." % (index_name))
        res = es_client.indices.delete(index=index_name)
        print(" response: '%s'" % (res))
    # since we are running locally, use one shard and no replicas
    request_body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    print("creating '%s' index..." % (index_name))
    res = es_client.indices.create(index=index_name, body=request_body)
    print(" response: '%s'" % (res))


class GraEntry(DocType):
    # TODO: add page number
    sort_id = Integer()
    headword_slp1 = Keyword(fields={'raw': Keyword()})
    headword_iso = Keyword(fields={'raw': Keyword()})
    headword_hk = Keyword(fields={'raw': Keyword()})
    headword_deva = Keyword(fields={'raw': Keyword()})
    headword_gra = Keyword(fields={'raw': Keyword()})
    headword_ascii = Keyword(fields={'raw': Keyword()})

    # some entries have homographs, most of the time, they should be subetries
    hom = Boolean()
    hom_number = Integer()

    entry_tei_iso = Text(analyzer=html_strip)
    entry_tei_gra = Text(analyzer=html_strip)
    sense = Text(analyzer=html_strip)
    created = Date()

    def save(self, **kwargs):
        return super(GraEntry, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.created


def prepare_entry_for_index(entry):
    entry = etree.tostring(entry, encoding='unicode')
    ##avoid too many whitespaces
    entry = ' '.join(entry.split())
    # normalize
    entry = unicodedata.normalize('NFC', entry)

    return entry


def prepare_gra_for_index(entry):
    # get headword in gra_notation
    boo = r'.)'
    rgx = re.compile('[%s]' % boo)
    gra_headword = entry.xpath('./ns:sense/ns:hi', namespaces=namespaces)[0]

    # process sense
    gra_sense = entry.xpath('./ns:sense', namespaces=namespaces)[0]
    gra_sense = etree.tostring(gra_sense, encoding='unicode')
    soup = BeautifulSoup(gra_sense, 'lxml')
    gra_sense = soup.get_text()
    # remove \n
    gra_sense = gra_sense.replace('\n', '')

    # process headword
    gra_headword = rgx.sub('', gra_headword.text)
    gra_headword = gra_headword.strip(string.punctuation)
    # remove pronunciation mark '-' from lemma
    gra_headword = gra_headword.replace('-', '')

    if ' ' in gra_headword:
        gra_headword = gra_headword.split()
        gra_headword = [e.strip(string.punctuation) for e in gra_headword]

    gra_entry = etree.tostring(entry, encoding='unicode')
    #entries in gra.xml have too many whitespaces
    gra_entry = ' '.join(gra_entry.split())
    # '|' is used in the transcription to mark a line break within a word
    gra_entry = gra_entry.replace('|', '')

    # normalize
    if isinstance(gra_headword, list):
        gra_headword = [unicodedata.normalize('NFC', e) for e in gra_headword]
    gra_entry = unicodedata.normalize('NFC', gra_entry)

    return gra_entry, gra_headword, gra_sense


def gra_entry_to_iso(entry):
    s = entry
    if 'ç' in s:
        s = s.replace('ç', 'ś')
    if 'Ç' in s:
        s = s.replace('Ç', 'Ś')
    # alle Vokale + circumflex sollten zu Vokal + Macron + Acute werden
    if 'â' in s:
        s = s.replace('â', 'ā́')
    if 'Â' in s:
        s = s.replace('Â', 'Ā́')
    if 'ê' in s:
        s = s.replace('ê', 'ḗ')
    if 'Ê' in s:
        s = s.replace('Ê', 'Ḗ')
    if 'î' in s:
        s = s.replace('î', 'ī́')
    if 'Î' in s:
        s = s.replace('Î', 'Ī́')
    if 'ô' in s:
        s = s.replace('ô', 'ṓ')
    if 'Ô' in s:
        s = s.replace('Ô', 'Ṓ')
    if 'û' in s:
        s = s.replace('û', 'ū́')
    if 'Û' in s:
        s = s.replace('Û', 'Ū́')
    # ṙ > r˳
    if 'ṙ' in s:
        s = s.replace('ṙ', 'r̥')
    if 'Ṙ' in s:
        s = s.replace('Ṙ', 'R̥')
    # ŕ > r˳́
    if 'ŕ' in s:
        s = s.replace('ṙ', 'ŕ̥')
    if 'Ŕ' in s:
        s = s.replace('Ŕ', 'Ŕ̥')

    s = unicodedata.normalize('NFC', s)

    return s


def get_tei_entries(grassmann):
    tree = etree.parse(grassmann)
    r = tree.xpath('/ns:TEI/ns:text/ns:body/ns:entry', namespaces=namespaces)
    print('len_entries', len(r))
    return r


def transliterate_slp1_into_iso(to_trans, conv):
    for k in conv:
        if k in to_trans:
            to_conv = conv.get(k)
            to_trans = to_trans.replace(k, to_conv)

    return to_trans


def index_entries(index_name, entries, conv):
    for i, e in enumerate(entries):
        headword_slp1 = e.xpath('./ns:form/ns:orth', namespaces=namespaces)[0].text
        print(headword_slp1)
        # normalize_slp1
        headword_slp1 = unicodedata.normalize('NFC', headword_slp1)
        # transliterate and normalize the rest
        headword_deva = xsanscript.transliterate(headword_slp1, scheme_map=scheme_slp1_deva)
        headword_hk = xsanscript.transliterate(headword_slp1, scheme_map=scheme_slp1_hk)
        headword_iso = transliterate_slp1_into_iso(headword_slp1, conv)
        headword_ascii = unidecode(headword_iso)

        headword_deva = unicodedata.normalize('NFC', headword_deva)
        headword_hk = unicodedata.normalize('NFC', headword_hk)
        headword_iso = unicodedata.normalize('NFC', headword_iso)
        # not necessary, but...
        headword_ascii = unicodedata.normalize('NFC', headword_ascii)

        # homographs
        milestone = e.xpath('./ns:form/ns:milestone', namespaces=namespaces)
        if milestone:
            hom = milestone[0].attrib['unit']
            hom_num = milestone[0].attrib['n']
            if hom != 'hom':
                print('oops', headword_slp1)

        # entry_form_hyph = e.xpath('./form/hyph')[0].text
        tei_entry = e.xpath('.')[0]

        if index_name == 'gra':
            tei_entry, headword_gra, sense_gra = prepare_gra_for_index(tei_entry)
            entry_to_index = GraEntry(
                meta={'id': e.attrib['{http://www.w3.org/XML/1998/namespace}id'], 'index': index_name})

        else:
            tei_entry = prepare_entry_for_index(tei_entry)
            entry_to_index = StandardEntry(
                meta={'id': e.attrib['{http://www.w3.org/XML/1998/namespace}id'], 'index': index_name})

        entry_to_index.sort_id = e.xpath('./ns:note/ns:idno', namespaces=namespaces)[0].text
        entry_to_index.headword_slp1 = headword_slp1
        entry_to_index.headword_deva = headword_deva
        entry_to_index.headword_hk = headword_hk
        entry_to_index.headword_iso = headword_iso
        entry_to_index.headword_ascii = headword_ascii

        if index_name == 'gra':
            entry_to_index.headword_gra = headword_gra
            entry_to_index.sense = sense_gra
            entry_to_index.entry_tei_gra = tei_entry
            entry_to_index.entry_tei_iso = gra_entry_to_iso(tei_entry)

        else:
            entry_to_index.entry_tei_iso = tei_entry

        if milestone:
            entry_to_index.hom = True
            entry_to_index.hom_number = hom_num
        else:
            entry_to_index.hom = False

        entry_to_index.created = datetime.now()
        entry_to_index.save()


def get_slp1_to_iso_mapping(slp1_to_roman):
    tree = etree.parse(slp1_to_roman)
    r = tree.xpath('e')
    d = {}
    for e in r:
        input = e.xpath('./in')[0]
        output = e.xpath('./out')[0]
        out = output.text
        out = bytes(out, "utf-8").decode("unicode_escape")
        out = normalize('NFC', out)
        d[input.text] = out
    return d


def index_file(index_name, slp1_to_iso, tei_file):
    if index_name == 'gra':
        GraEntry.init(index_name)
    else:
        StandardEntry.init(index_name)

    entries = get_tei_entries(tei_file)
    index_entries(index_name, entries, slp1_to_iso)
    print('done with it')


def delete_index(index_name):
    to_del = Index(index_name)
    # delete the index, ignore if it doesn't exist
    to_del.delete(ignore=404)


def del_and_re_index(index_name, tei_to_index, slp1_iso_mapping):
    print('deleting index:  ', index_name)
    delete_index(index_name)
    slp1_to_iso = get_slp1_to_iso_mapping(slp1_iso_mapping)
    print('creating index:  ', index_name)
    index_file(index_name, slp1_to_iso, tei_to_index)
