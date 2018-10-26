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


class BHSEntry(DocType):
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
        index = 'bhs'

    def save(self, **kwargs):
        return super(BHSEntry, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.created


def prepare_gra_for_index(entry):
    # get headword in gra_notation

    boo = r'.)'
    rgx = re.compile('[%s]' % boo)
    bhs_headword = entry.xpath('./ns:sense/ns:hi', namespaces=namespaces)[0]
    bhs_headword = rgx.sub('', bhs_headword.text)
    # bhs_headword = etree.tostring(bhs_headword, encoding='unicode')
    bhs_headword = bhs_headword.strip(string.punctuation)
    # remove pronunciation mark '-' from lemma
    bhs_headword = bhs_headword.replace('-', '')

    if ' ' in bhs_headword:
        bhs_headword = bhs_headword.split()
        bhs_headword = [e.strip(string.punctuation) for e in bhs_headword]

    bhs_entry = etree.tostring(entry, encoding='unicode')
    ##entries in gra.xml have too many whitespaces
    bhs_entry = ' '.join(bhs_entry.split())
    # '|' is used in the transcription to mark a line break within a word
    bhs_entry = bhs_entry.replace('|', '')
    bhs_entry = bhs_entry.replace('<lb/>', '</br>')
    bhs_entry = re.sub(r'<hi rendition="#b">(.*?)</hi>', r'<b>\1</b>', bhs_entry,
                       flags=re.DOTALL)
    bhs_entry = re.sub(r'<hi rendition="#i">(.*?)</hi>', r'<i>\1</i>', bhs_entry,
                       flags=re.DOTALL)
    bhs_entry = re.sub(r'<hi rendition="#center">(.*?)</hi>', r'<div style="text-align:center>\1</div>', bhs_entry,
                       flags=re.DOTALL)

    # normalize
    if isinstance(bhs_headword, list):
        bhs_headword = [unicodedata.normalize('NFC', e) for e in bhs_headword]
    bhs_entry = unicodedata.normalize('NFC', bhs_entry)

    return bhs_entry, bhs_headword


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
        tei_entry, headword_gra = prepare_gra_for_index(tei_entry)

        bhs_entry_to_index = BHSEntry(meta={'id': e.attrib['{http://www.w3.org/XML/1998/namespace}id']})
        bhs_entry_to_index.sort_id = e.xpath('./ns:note/ns:idno', namespaces=namespaces)[0].text
        bhs_entry_to_index.headword_slp1 = headword_slp1
        bhs_entry_to_index.headword_deva = headword_deva
        bhs_entry_to_index.headword_hk = headword_hk
        bhs_entry_to_index.headword_iso = headword_iso
        bhs_entry_to_index.headword_gra = headword_gra
        bhs_entry_to_index.headword_ascii = headword_ascii

        if milestone:
            bhs_entry_to_index.hom = True
            bhs_entry_to_index.hom_number = hom_num
        else:
            bhs_entry_to_index.hom = False
        bhs_entry_to_index.entry_tei_gra = tei_entry

        bhs_entry_to_index.created = datetime.now()
        bhs_entry_to_index.save()


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


def format_entries():
    entries = get_bhs_entries('data/gra_csl_with_greek_words.xml')
    for e in entries:
        entry_entry = e.xpath('./entry')[0]
        out = etree.tostring(entry_entry, encoding='unicode', pretty_print=True)
        ##entries in gra.xml have too many whitespaces
        out = ' '.join(out.split())
        out = re.sub(r'<hi rendition="#b">(.*?)</hi>', r'<b>\1</b>', out,
                     flags=re.DOTALL)
        out = re.sub(r'<hi rendition="#i">(.*?)</hi>', r'<i>\1</i>', out,
                     flags=re.DOTALL)
        out = re.sub(r'<hi rendition="#center">(.*?)</hi>', r'<div style="text-align:center>\1</div>', out,
                     flags=re.DOTALL)
        print(out)


def test_transliterate_slp1_deva(to_trans, conv):
    output = xsanscript.transliterate(to_trans, scheme_map=scheme_slp1_deva)
    # romanised_unicode = iso15919.transliterate(output)
    iso = transliterate_slp1_into_iso(to_trans, conv)
    print(to_trans, output, iso)


def transliterate_iast_slp1(input):
    output = xsanscript.transliterate(input, scheme_map=scheme_iast_slp1)
    return output


def index_bhs(conv, bhs_tei):
    BHSEntry.init()
    entries = get_bhs_entries(bhs_tei)
    index_entries(entries, conv)
    print('done with it')


def delete_index(to_del):
    index_name = Index(to_del)
    # delete the index, ignore if it doesn't exist
    index_name.delete(ignore=404)


def del_and_re_index_bhs(bhs_tei, slp1_iso_mapping):
    delete_index('bhs')
    conv = get_slp1_to_iso_mapping(slp1_iso_mapping)
    index_bhs(conv, bhs_tei)


slp1_iso_mapping = '../../../utils/slp1_romanpms.xml'
bhs_dir = '../../../../c-salt_sanskrit_data/sa_en/bhs/'
bhs_tei = bhs_dir + 'bhs.tei'

del_and_re_index_bhs(bhs_tei, slp1_iso_mapping)
