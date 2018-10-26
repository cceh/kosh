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

ducet_analyzer = analyzer('ducet_sort',
                          tokenizer="icu_tokenizer",
                          filter=["icu_folding", "lowercase"],
                          char_filter=["html_strip"]
                          )

html_strip = analyzer('html_strip',
                      tokenizer="standard",
                      filter=["standard", "lowercase"],
                      char_filter=["html_strip"]
                      )


class PWGEntry(DocType):
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
        index = 'pwg'

    def save(self, **kwargs):
        return super(PWGEntry, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.created


def get_entries(monier):
    tree = etree.parse(monier)
    r = tree.xpath('/TEI/text/body/div/entry')
    print(len(r))
    return r


def transliterate_slp1_into_iso(to_trans, conv):
    for k in conv:
        if k in to_trans:
            to_conv = conv.get(k)
            to_trans = to_trans.replace(k, to_conv)

    return to_trans


def index_entries(entries, conv):
    for e in entries:
        headword_slp1 = e.xpath('./form/orth')[0].text
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
        milestone = e.xpath('./form/milestone')
        if milestone:
            hom = milestone[0].attrib['unit']
            hom_num = milestone[0].attrib['n']
            if hom != 'hom':
                print('oops', headword_slp1)

        # entry_form_hyph = e.xpath('./form/hyph')[0].text
        tei_entry = e.xpath('.')[0]

        gra_entry_to_index = PWGEntry(meta={'id': e.attrib['{http://www.w3.org/XML/1998/namespace}id']})
        gra_entry_to_index.sort_id = e.xpath('./note/idno')[0].text
        gra_entry_to_index.headword_slp1 = headword_slp1
        gra_entry_to_index.headword_deva = headword_deva
        gra_entry_to_index.headword_hk = headword_hk
        gra_entry_to_index.headword_iso = headword_iso
        gra_entry_to_index.headword_ascii = headword_ascii

        if milestone:
            gra_entry_to_index.hom = True
            gra_entry_to_index.hom_number = hom_num
        else:
            gra_entry_to_index.hom = False
        gra_entry_to_index.entry_tei_iso = tei_entry

        gra_entry_to_index.created = datetime.now()
        gra_entry_to_index.save()


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


def index_pwg(conv):
    PWGEntry.init()
    entries = get_entries('../../data/lazarus/pwg.tei')
    index_entries(entries, conv)
    print('done with it')


def delete_index(to_del):
    index_name = Index(to_del)
    # delete the index, ignore if it doesn't exist
    index_name.delete(ignore=404)


def del_and_re_index_pwg():
    # delete_index('monier')
    conv = get_slp1_to_iso_mapping('../../data/slp1_romanpms.xml')
    index_pwg(conv)


del_and_re_index_pwg()
