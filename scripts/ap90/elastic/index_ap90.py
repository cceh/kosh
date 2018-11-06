import re
import string
import unicodedata
from datetime import datetime
from unicodedata import normalize
from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, Date, Keyword, Text, Integer, Boolean, connections, analyzer, Index
from indic_transliteration import xsanscript
from indic_transliteration.xsanscript import SchemeMap, SCHEMES, HK, SLP1, DEVANAGARI, IAST
from unidecode import unidecode
from lxml import etree

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


class AP90Entry(DocType):
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

    class Meta:
        index = 'ap90'

    def save(self, **kwargs):
        return super(AP90Entry, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.created


def prepare_entry_for_index(entry):
    entry_to_index = etree.tostring(entry, encoding='unicode')
    ##entries in gra.xml have too many whitespaces
    entry_to_index = ' '.join(entry_to_index.split())
    # normalize
    entry_to_index = unicodedata.normalize('NFC', entry_to_index)

    return entry_to_index


def get_bhs_entries(bhs_tei):
    tree = etree.parse(bhs_tei)
    r = tree.xpath('/ns:TEI/ns:text/ns:body/ns:entry', namespaces=namespaces)
    print('len_tree', len(r))
    return r


def transliterate_slp1_into_iso(to_trans, conv):
    for k in conv:
        if k in to_trans:
            to_conv = conv.get(k)
            to_trans = to_trans.replace(k, to_conv)

    return to_trans


def index_entries(entries, conv):
    for e in entries:
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

        ap90_entry_to_index = AP90Entry(meta={'id': e.attrib['{http://www.w3.org/XML/1998/namespace}id']})
        ap90_entry_to_index.sort_id = e.xpath('./ns:note/ns:idno', namespaces=namespaces)[0].text
        ap90_entry_to_index.headword_slp1 = headword_slp1
        ap90_entry_to_index.headword_deva = headword_deva
        ap90_entry_to_index.headword_hk = headword_hk
        ap90_entry_to_index.headword_iso = headword_iso
        ap90_entry_to_index.headword_ascii = headword_ascii

        if milestone:
            ap90_entry_to_index.hom = True
            ap90_entry_to_index.hom_number = hom_num
        else:
            ap90_entry_to_index.hom = False

        ap90_entry_to_index.entry_tei_iso = prepare_entry_for_index(tei_entry)

        ap90_entry_to_index.created = datetime.now()
        ap90_entry_to_index.save()


def get_slp1_to_iso_mapping(slp1_to_roman):
    tree = etree.parse(slp1_to_roman)
    r = tree.xpath('e')
    # print(len(r))
    d = {}
    for e in r:
        input = e.xpath('./in')[0]
        output = e.xpath('./out')[0]
        out = output.text
        out = bytes(out, "utf-8").decode("unicode_escape")
        out = normalize('NFC', out)

        # if get_char_names(out):
        #    print(input.text, out, get_char_names(out))
        # else:
        #    print(input.text, out, 'NO UNICODE NAME')

        d[input.text] = out

    return d


def test_transliterate_slp1_deva(to_trans, conv):
    output = xsanscript.transliterate(to_trans, scheme_map=scheme_slp1_deva)
    # romanised_unicode = iso15919.transliterate(output)
    iso = transliterate_slp1_into_iso(to_trans, conv)
    print(to_trans, output, iso)


def transliterate_iast_slp1(input):
    output = xsanscript.transliterate(input, scheme_map=scheme_iast_slp1)
    return output


def index_ap90(conv, bhs_tei):
    AP90Entry.init()
    entries = get_bhs_entries(bhs_tei)
    index_entries(entries, conv)
    print('done with it')


def delete_index(to_del):
    index_name = Index(to_del)
    # delete the index, ignore if it doesn't exist
    index_name.delete(ignore=404)


def del_and_re_index_ap90(ap90_tei, slp1_iso_mapping):
    delete_index('ap90')
    conv = get_slp1_to_iso_mapping(slp1_iso_mapping)
    index_ap90(conv, ap90_tei)


slp1_iso_mapping = '../../../utils/slp1_romanpms.xml'
base_dir = '../../../../c-salt_sanskrit_data/sa_en/ap90/'
ap90_tei = base_dir + 'ap90.tei'

del_and_re_index_ap90(ap90_tei, slp1_iso_mapping)
