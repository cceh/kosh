import collections
import re
import shutil
from os import listdir
from os.path import basename
from os.path import isfile, join
from unicodedata import name, normalize

from lxml import etree
from pymongo import MongoClient
from pyuca import Collator

from utils import input_output

# Required mapping
nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}


def get_collection(database, collection):
    client = MongoClient()
    db = client[database]
    collection = db[collection]
    return collection


def grassmann_into_mongo(rv_raw):
    grassmann = get_collection('vedaweb', 'grassmann')
    for e in rv_raw.find():
        lemma = e.get('lemmata klassisch::lemma')
        lemmatyp = e.get('lemmata klassisch::lemmatyp')
        bedeutung = e.get('lemmata klassisch::bedeutung')
        HELPbedeutung = e.get('lemmata klassisch::HELPbedeutung')

        data = dict()

        if lemma is not None:
            data.update({'lemma': lemma.strip()})
        if lemmatyp is not None and lemmatyp is not '':
            data.update({'lemmatyp': lemmatyp.strip()})
        if bedeutung is not None and bedeutung is not '':
            data.update({'bedeutung': bedeutung.strip()})
        if HELPbedeutung is not None and HELPbedeutung is not '':
            data.update({'HELPbedeutung': HELPbedeutung.strip()})

        grassmann.insert_one(data)

    return grassmann


def delete_duplicates(grassmann):
    lemmata = set()
    counter = 0
    for e in grassmann.find():
        counter += 1
        try:
            lemma = e.get('lemma')
            lemmatyp = e.get('lemmatyp')
            bedeutung = e.get('bedeutung')

            if ',' in bedeutung and ';' not in bedeutung:
                bedeutung = bedeutung.split(',')
                # print('1', lemma, bedeutung)
            if ';' in bedeutung and ',' not in bedeutung:
                bedeutung = bedeutung.split(';')
                # print('2', lemma, bedeutung)
            if ',' in bedeutung and ';' in bedeutung:
                bedeutung = bedeutung.split(';')
                # print('3', lemma, bedeutung)

            else:
                pass
                # print('4', lemma, bedeutung)

            if type(bedeutung) is str:
                entry = (lemma, lemmatyp, bedeutung)
            else:
                entry = (lemma, lemmatyp, tuple(bedeutung))
            lemmata.add(entry)

        except TypeError as err:
            pass
            # print(lemma, bedeutung, err)
            # break
    print('entries in rv_raw', counter)
    return lemmata


def get_lemmata_from_grassmann_zuerich():
    grassmann = get_collection('vedaweb', 'grassmann')
    lemmata = set()
    boo = r'\d+√-'
    rgx = re.compile('[%s]' % boo)
    for e in grassmann.find():
        lemma = e.get('lemma')
        # lemma = ''.join(c for c in lemma if c not in '√-')
        lemma = rgx.sub('', lemma)
        lemma = lemma.strip()
        lemmata.add(lemma)
    return lemmata


def get_list_lemmata_mongo(entries):
    lemmata = []
    sorted_by_first = sorted(entries, key=lambda tup: tup[0])

    for s in sorted_by_first:
        lemmata.append(s[0])

    return lemmata


def grassmann_zuerich_into_tei(grassmann):
    root = etree.Element("root")
    for e in grassmann:
        try:
            # print(e)

            entry = etree.SubElement(root, "entry")
            form = etree.SubElement(entry, "form")
            etree.SubElement(form, 'orth').text = e[0]

            gramgrp = etree.SubElement(entry, 'gramGrp')
            etree.SubElement(gramgrp, 'pos').text = e[1]

            senses = e[2]
            if type(senses) is tuple:
                counter = 0
                for s in senses:
                    counter += 1
                    sense_elem = etree.SubElement(entry, 'sense', n=str(counter))
                    etree.SubElement(sense_elem, 'def').text = s.strip()
            else:
                sense_elem = etree.SubElement(entry, 'sense')
                etree.SubElement(sense_elem, 'def').text = senses.strip()

        except TypeError as err:
            print(err)

    tree = etree.ElementTree(root)
    print(tree)
    tree.write(open('data/grassmann_2.tei', 'wb'), encoding='utf-8', pretty_print=True)


def get_gra_ids(grassmann_xml):
    tree = etree.parse(grassmann_xml)
    r = tree.xpath('/gra')[0]
    r.tag = 'body'
    ids = []
    for i, e in enumerate(r):
        e.tag = 'entry'
        try:
            for child in e:
                # process lemma_info
                if child.tag == 'h':
                    child.tag = 'form'
                    for h in child:
                        if h.tag == 'key1':
                            l_n = e.xpath('./tail/L')
                            _id = 'lemma_' + h.text + '_' + l_n[0].text
                            ids.append(_id)
        except Exception as exc:
            print(e, exc)

    return ids


def grassmann_csl_into_tei(grassmann_xml, path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('col')]

    tree = etree.parse(grassmann_xml)

    # root = tree.getroot()
    rut = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})
    r = tree.xpath('/gra')[0]
    r.tag = 'body'

    # modify entries
    for i, e in enumerate(r):
        e.tag = 'entry'
        try:
            for child in e:
                # process lemma_info
                if child.tag == 'h':
                    child.tag = 'form'
                    for h in child:
                        if h.tag == 'key1':
                            h.tag = 'orth'
                            h.attrib['ana'] = 'key1'
                            h.attrib['type'] = 'transliterated'
                            # http://bendustries.org/wp/?p=21
                            h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"
                            # set form id
                            l_n = e.xpath('./tail/L')
                            e.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'lemma_' + h.text + '_' + l_n[
                                0].text
                        if h.tag == 'key2':
                            child.remove(h)
                            # h.tag = 'hyph'
                            # h.attrib['ana'] = 'key2'
                            # h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"

                        if h.tag == 'hom':
                            # <hom>1</hom> : <milestone unit="hom" n="1"/>
                            hom_value = h.text
                            h.text = None
                            h.tag = 'milestone'
                            h.attrib['unit'] = 'hom'
                            h.attrib['n'] = hom_value

                # process def_info
                if child.tag == 'body':
                    child.tag = 'sense'
                    for b in child:
                        if b.tag == 'i':
                            # < hi rendition = "#i" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#i'

                        if b.tag == 'b':
                            # < hi rendition = "#b" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#b'

                        if b.tag == 'wide':
                            # < hi rendition = "#wide" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#wide'

                        # greek empty tags
                        if b.tag == 'g':
                            b.tag = 'w'
                            b.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'el'
                            b.text = ' '
                        # only one footnote in the whole dict
                        if b.tag == 'F':
                            b.tag = 'note'
                            b.attrib['place'] = 'foot'
                            # not possible with the current schema:
                            # b.attrib['type'] = 'footnote'
                        # not consistent difference between paragraph and subpararaph. On the layout is this simply a line break

                        if b.tag == 'P1' or b.tag == 'P':
                            b.tag = 'lb'

                # process tail_info
                if child.tag == 'tail':
                    child.tag = 'note'
                    for t in child:
                        # <idno ana="L" xml:id="gra_79">79</idno>
                        if t.tag == 'L':
                            t.tag = 'idno'
                            t.attrib['ana'] = 'L'
                            t.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'gra_' + t.text

                        # <tail><L>79</L><pc>0008</pc></tail>
                        if t.tag == 'pc':
                            t.tag = 'ref'
                            t.attrib['type'] = 'facs'

                            for col in pages:
                                if t.text in str(col):
                                    t.attrib['target'] = col.replace(path_to_pages, '#')





        except TypeError as err:
            print(err)

    # add header info
    header = etree.Element("teiHeader")
    file_desc = etree.SubElement(header, 'fileDesc')

    title_stmt = etree.SubElement(file_desc, 'titleStmt')
    title = etree.SubElement(title_stmt, 'title')
    title.text = 'Wörterbuch zum Rig-veda - Grassmann (1873)'

    publication_stmt = etree.SubElement(file_desc, 'publicationStmt')
    p_publisher = etree.SubElement(publication_stmt, 'p')
    p_publisher.text = 'CCeH - Cologne Center for eHumanities - 2018'

    source_desc = etree.SubElement(file_desc, 'sourceDesc')
    p_source_desc = etree.SubElement(source_desc, 'p')
    p_source_desc.text = 'XML file - Cologne Digital Sanskrit Dictionaries'

    # add facs info
    # <facsimile><graphic url="scans/ae-vor-01" xml:id="page-title-1"/>

    facs = etree.Element("facsimile")
    for p in pages:
        etree.SubElement(facs, 'graphic',
                         attrib={"url": "scans/" + basename(p),
                                 "{http://www.w3.org/XML/1998/namespace}id": basename(p)})

    text = etree.Element("text")
    text.append(r)
    rut.append(header)
    rut.append(facs)
    rut.append(text)

    et = etree.ElementTree(rut)

    return et


def add_centered_tags(grassman_tei):
    with open(grassman_tei, mode='r') as file:
        data = file.read()
        data = re.sub(r'§§<lb/>', r'<lb/>   ', data, flags=re.DOTALL)
        counter_a = 0;
        counter_b = 0;

        for e in re.findall(r'<H/>(.*?)<lb/>', data, re.DOTALL):
            if '<H/>' in e:
                counter_a += 1
                mod_s = e
                mod_s = mod_s.replace('<H/>', '<lb/><H/>')
                # print(mod_s)
                data = data.replace(e, mod_s)

        data = re.sub(r'<H/>(.*?)<lb/>', r'<lb/><hi rendition="#center">\1</hi><lb/>', data, flags=re.DOTALL)
        # data = re.sub(r'<H/>(.*?)</sense>', r'<lb/><hi rendition="#center">\1</hi><lb/></sense>', data, flags=re.DOTALL)
        # data = re.sub(r'§§<lb/>', r'<lb/>   ', data);

        print(counter_a)

    return data


def clean_up_tags(grassman_tei):
    with open(grassman_tei, mode='r') as file:
        data = file.read()
        data = re.sub(r'§§<lb/>', r'<lb/>   ', data, flags=re.DOTALL)

        for e in re.findall(r'<sense>(.*?)</sense>', data, re.DOTALL):

            mod_s = e

            if '<H/>' in e:
                mod_s = mod_s.replace('<H/>', '<lb/><H/>')

            if re.search(r'<H/>(.*?)<lb/>', mod_s, re.DOTALL):
                mod_s = re.sub(r'<H/>(.*?)<lb/>', r'<hi rendition="#center">\1</hi><lb/>', mod_s,
                               flags=re.DOTALL)

            if re.search(r'<H/>(.*?)$', mod_s, re.DOTALL):
                mod_s = re.sub(r'<H/>(.*?)$', r'<hi rendition="#center">\1</hi><lb/>', mod_s,
                               flags=re.DOTALL)

            data = data.replace(e, mod_s)

    return data


def rename_pdf_files(path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('pg')]

    for e in pages:
        or_bn = e
        bn = e
        bn_n = re.findall('\d+', bn)[0]
        added_col = int(bn_n) + 1
        bn = bn.replace(str(bn_n), str(bn_n) + '_' + str(added_col).zfill(4)).replace('pg', 'col')
        shutil.move(or_bn, bn)
        # print(e)


def decode_diacritics(diacritics, grassman_tei):
    grassmann = input_output.file_to_list(grassman_tei)
    processed = []

    for line in grassmann:
        # we split every line
        line = line.split()
        # process every string
        for i, s in enumerate(line):

            if 'a10' in s:
                s = s.replace('a10', 'a6')
            if 'a11' in s:
                s = s.replace('a11', 'a7')
            if 'a14' in s:
                s = s.replace('a14', 'a8')
            if 'e10' in s:
                s = s.replace('e10', 'e2')
            if 'i10' in s:
                s = s.replace('i10', 'i2')
            if 'i13' in s:
                s = s.replace('i13', 'i5')
            if 'o10' in s:
                s = s.replace('o10', 'o8')
            if 'r10' in s:
                s = s.replace('r10', 'r5')
            if 'u10' in s:
                s = s.replace('u10', 'u2')
            if 'u11' in s:
                s = s.replace('u11', 'u3')

            for d in diacritics:
                # if diac in string
                p = re.compile(d + r'(?!\d+|>|")')
                match_object = re.search(p, s)
                if match_object:
                    # replace it
                    s = s.replace(d, diacritics.get(d))
                    line[i] = s

            # replace grassmann's own chars with standarized ones
            # replace ç with ś

            line[i] = s

        processed.append(" ".join(line))

    return processed


def get_diacritics(path_to_diacritics):
    with open(path_to_diacritics, mode='r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        d = {}
        for l in lines:
            l = l.split()
            d[l[0]] = l[3]

    return d


def get_greek_tags(grassmann):
    tree = etree.parse(grassmann)
    r = tree.xpath('/TEI/text/body/entry/sense/w')
    # greek_entries = {}
    greek_entries = collections.OrderedDict()
    for e in r:
        sense = e.getparent()
        entry = sense.getparent()
        en = entry.get('{http://www.w3.org/XML/1998/namespace}id')
        # print(etree.tounicode(entry))
        # print(etree.tostring(en))
        greek_entries[en] = etree.tounicode(e)
    return greek_entries


def get_lemmata_slp1(grassmann_tei):
    lemmata_slp1 = []
    tree = etree.parse(grassmann_tei)
    r = tree.xpath('/TEI/text/body/entry/form/orth')
    for e in r:
        lemmata_slp1.append(e.text)

    return lemmata_slp1


def get_lemmata_grassmannische_notation(grassmann_tei):
    lemmata = []
    tree = etree.parse(grassmann_tei)
    r = tree.xpath('/TEI/text/body/entry/sense')
    boo = r'.)'
    rgx = re.compile('[%s]' % boo)
    for e in r:
        # we get the first <hi rendition="#b"> element
        # entry = e.getparent()
        # en = entry.get('{http://www.w3.org/XML/1998/namespace}id')
        hi_en = e.xpath('./hi')[0]

        lemma = rgx.sub('', hi_en.text)
        lemma = lemma.strip(',')
        lemma = lemma.strip()
        lemmata.append(lemma)

    return lemmata


def get_char_names(s):
    try:
        char_names = [name(c) for c in s]

    except ValueError:

        char_names = None

    return char_names


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


def get_slp1_to_iso_mapping_2(slp1_to_roman):
    d = {}

    with open(slp1_to_roman, mode='rb') as file:
        as_list = file.read().splitlines()
        for line in as_list:
            print(repr(line.decode('unicode_escape')))

    return d


def transliterate_lemmata(lemmata_slp1, conv):
    transliterated = []
    for l in lemmata_slp1:
        for k in conv:
            if k in l:
                # print(l, k, conv.get(k))
                to_conv = conv.get(k)
                l = l.replace(k, to_conv)

        transliterated.append(l)

    return transliterated


def process_greek_references(to_process):
    dict = {}
    with open(to_process, mode='r') as file:
        as_list = file.read().splitlines()
        for e in as_list:
            line = e.split('\t')
            lemma = line[0]
            lemma_id = lemma.split('_')[2]
            new_lemma = lemma.replace(lemma_id, str(int(lemma_id) + 1))
            gr_lemmata = line[1].split(';')

            dict[new_lemma] = gr_lemmata

    return dict


def add_gr_data(grassmann_tei, gr_data):
    tree = etree.parse(grassmann_tei)

    for e in gr_data:
        # print(e, gr_data.get(e))
        gr_entry = tree.xpath("/TEI/text/body/entry[@xml:id='" + e + "']/sense/w[@xml:lang='el']")

        if len(gr_entry) != len(gr_data.get(e)):
            print(e, len(gr_entry), len(gr_data.get(e)))
        else:
            to_fill_with = gr_data.get(e)
            # the second element of this entry contains a word in hebrew
            if e == 'lemma_naqa_4812':
                gr_0 = gr_entry[0]
                gr_0.text = to_fill_with[0].strip()
                gr_1 = gr_entry[1]
                gr_1.text = to_fill_with[1].strip()
                # set attrbute to lang = hebrew
                gr_1.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'he'

            else:
                for i, w in enumerate(gr_entry):
                    w.text = to_fill_with[i].strip()

    return tree


def sort_unicode_collation_algorithm(list_to_sort):
    c = Collator()
    sorted_list = sorted(list_to_sort, key=c.sort_key)
    return sorted_list


def grassmann_zuerich():
    # rv_raw = get_collection('vedaweb', 'rv_raw')
    # grassmann_into_mongo(rv_raw)

    grassmann = get_collection('vedaweb', 'grassmann')
    entries = delete_duplicates(grassmann)
    grassmann_zuerich_into_tei(entries)


def process_grassmann(gra_dir):
    gra_csl_base = grassmann_csl_into_tei(gra_dir + 'gra.xml', gra_dir + 'gra_pages/')
    gra_csl_base.write('../data/gra_csl_base.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")
    print('step_1_done')

    # remove emtpy tags such as <H/>
    gra_csl_with_cleaned_tags = clean_up_tags('../data/gra_csl_base.xml')
    input_output.to_file('../data/gra_csl_with_cleaned_tags.xml', gra_csl_with_cleaned_tags)
    print('step_2_done')

    # replace Molten's ASCII-based notation with its ISO counterpart
    diacs = get_diacritics('../data/gra_to_diacs.txt')
    gra_csl_decoded = decode_diacritics(diacs, '../data/gra_csl_with_cleaned_tags.xml')
    input_output.print_list('../data/gra_csl_decoded.xml', gra_csl_decoded)
    print('step_3_done')

    greek_entries_filled = process_greek_references('../data/entries_with_gr_tags_filled_1')
    root = add_gr_data('../data/gra_csl_decoded.xml', greek_entries_filled)
    root.write(gra_dir + 'gra.tei', pretty_print=True, xml_declaration=True, encoding="utf-8")
    print('step_4_done')


def convert_slp1_lemmata_into_iso():
    entries_in_slp1 = get_lemmata_slp1('data/gra_csl_with_greek_words.xml')
    input_output.print_list('data/gra_csl_lemmata_slp1.txt', entries_in_slp1)
    conv = get_slp1_to_iso_mapping('data/slp1_romanpms.xml')
    transliterated = transliterate_lemmata(entries_in_slp1, conv)
    transliterated_sorted = sort_unicode_collation_algorithm(transliterated)
    input_output.print_list('data/gra_csl_lemmata_iso_sorted.txt', transliterated_sorted)
    transliterated = set(transliterated)
    transliterated = list(transliterated)
    transliterated_sorted = sort_unicode_collation_algorithm(transliterated)
    input_output.print_list('data/gra_csl_lemmata_iso_sorted_nodups.txt', transliterated_sorted)


def process_lemmata_grassmann_zuerich():
    grassmann_zuerich = get_lemmata_from_grassmann_zuerich()
    grassmann_zuerich = list(grassmann_zuerich)
    transliterated_sorted = sort_unicode_collation_algorithm(grassmann_zuerich)
    input_output.print_list('data/yū́yuvi.txt', transliterated_sorted)


def get_lemmata_grass_notation_csl():
    lemmata = get_lemmata_grassmannische_notation('data/gra_csl_with_greek_words.xml')
    lemmata_sorted = sort_unicode_collation_algorithm(lemmata)
    input_output.print_list('data/gra_csl_lemmata_grass_notation_sorted.txt', lemmata_sorted)
    lemmata = set(lemmata)
    lemmata = list(lemmata)
    lemmata = sort_unicode_collation_algorithm(lemmata)
    input_output.print_list('data/gra_csl_lemmata_grass_notation_sorted_nodups.txt', lemmata)


gra_dir = '../../../../c-salt_sanskrit_data/sa_de/gra/'

process_grassmann(gra_dir)
