import collections
import re
import shutil
from os import listdir
from os.path import basename
from os.path import isfile, join
from unicodedata import name, normalize

from lxml import etree
from utils import input_output

# Required mapping
nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}


def bhs_csl_into_tei(bhs_xml, path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('pg')]

    tree = etree.parse(bhs_xml)

    # root = tree.getroot()
    rut = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})
    r = tree.xpath('/bhs')[0]
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
                            # http://bendustries.org/wp/?p=21
                            h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"
                            # set form id
                            l_n = e.xpath('./tail/L')
                            e.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'lemma_' + h.text + '_' + l_n[
                                0].text
                        if h.tag == 'key2':
                            h.tag = 'hyph'
                            h.attrib['ana'] = 'key2'
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
                            for sub in b:
                                if sub.tag == 'br' or sub.tag == '':
                                    sub.tag = 'lb'

                        if b.tag == 'b':
                            # < hi rendition = "#b" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#b'
                            for sub in b:
                                if sub.tag == 'br' or sub.tag == '':
                                    sub.tag = 'lb'

                        if b.tag == 'wide':
                            # < hi rendition = "#wide" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#wide'
                            for sub in b:
                                if sub.tag == 'br' or sub.tag == '':
                                    sub.tag = 'lb'

                        # greek empty tags
                        if b.tag == 'g':
                            b.tag = 'w'
                            b.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = 'el'
                            b.text = ' '
                            for sub in b:
                                if sub.tag == 'br' or sub.tag == '':
                                    sub.tag = 'lb'

                        # only one footnote in the whole dict
                        if b.tag == 'F':
                            b.tag = 'note'
                            b.attrib['place'] = 'foot'
                            # b.attrib['type'] = 'footnote'
                            # not consistent difference between parabhsph and subpararaph. On the layout is this simply a line break
                            for sub in b:
                                if sub.tag == 'br' or sub.tag == '':
                                    sub.tag = 'lb'

                        if b.tag == 'P1' or b.tag == 'P':
                            b.tag = 'lb'

                        if b.tag == 'br':
                            b.tag = 'lb'

                # process tail_info
                if child.tag == 'tail':
                    child.tag = 'note'
                    for t in child:
                        # <idno ana="L" xml:id="bhs_79">79</idno>
                        if t.tag == 'L':
                            t.tag = 'idno'
                            t.attrib['ana'] = 'L'
                            t.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'bhs_' + t.text

                        # <tail><L>79</L><pc>0008</pc></tail>
                        if t.tag == 'pc':
                            t.tag = 'ref'
                            t.attrib['type'] = 'facs'

                            for page in pages:
                                page_number_and_column = t.text
                                page_number_and_column = page_number_and_column.split(',')
                                if page_number_and_column[0].zfill(3) in str(page):
                                    t.attrib['target'] = page.replace(path_to_pages, '#')






        except TypeError as err:
            print(err)

    # add facs info
    # <facsimile><bhsphic url="scans/ae-vor-01" xml:id="page-title-1"/>

    facs = etree.Element("facsimile")
    for p in pages:
        etree.SubElement(facs, 'graphic',
                         attrib={"url": "scans/" + basename(p),
                                 "{http://www.w3.org/XML/1998/namespace}id": basename(p)})

    text = etree.Element("text")
    text.append(r)

    # create header and append

    # add header info
    header = etree.Element("teiHeader")
    file_desc = etree.SubElement(header, 'fileDesc')

    title_stmt = etree.SubElement(file_desc, 'titleStmt')
    title = etree.SubElement(title_stmt, 'title')
    title.text = 'Buddhist hybrid sanskrit grammar and dictionary / 2. Dictionary - Edgerton (1953)'

    publication_stmt = etree.SubElement(file_desc, 'publicationStmt')
    p_publisher = etree.SubElement(publication_stmt, 'p')
    p_publisher.text = 'CCeH - Cologne Center for eHumanities - 2018'

    source_desc = etree.SubElement(file_desc, 'sourceDesc')
    p_source_desc = etree.SubElement(source_desc, 'p')
    p_source_desc.text = 'XML file - Cologne Digital Sanskrit Dictionaries'

    rut.append(header)
    rut.append(facs)
    rut.append(text)

    et = etree.ElementTree(rut)

    return et


def add_centered_tags(bhsssman_tei):
    with open(bhsssman_tei, mode='r') as file:
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


def clean_up_tags(bhsssman_tei):
    with open(bhsssman_tei, mode='r') as file:
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


def decode_diacritics(diacritics, bhsssman_tei):
    bhs = input_output.file_to_list(bhsssman_tei)
    processed = []

    for line in bhs:
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
                s = s.replace('e10', 'e5')
            if 'e11' in s:
                s = s.replace('e11', 'e2')
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
            if 'r21' in s:
                s = s.replace('r21', 'r3')

            for d in diacritics:
                # if diac in string
                p = re.compile(d + r'(?!\d+|>|")')
                match_object = re.search(p, s)
                if match_object:
                    # replace it
                    s = s.replace(d, diacritics.get(d))
                    line[i] = s

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


def get_lemmata_slp1(bhs_tei):
    lemmata_slp1 = []
    tree = etree.parse(bhs_tei)
    r = tree.xpath('/TEI/text/body/entry/form/orth')
    for e in r:
        lemmata_slp1.append(e.text)

    return lemmata_slp1


def get_lemmata_bhsische_notation(bhs_tei):
    lemmata = []
    tree = etree.parse(bhs_tei)
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


def process_bhs(bhs_dir):
    bhs_csl_base = bhs_csl_into_tei(bhs_dir + 'bhs.xml', bhs_dir + 'bhs_pages')
    bhs_csl_base.write('../data/bhs_csl_base.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")
    print('step_1_done')

    bhs_csl_with_cleaned_tags = clean_up_tags('../data/bhs_csl_base.xml')
    input_output.to_file('../data/bhs_csl_with_cleaned_tags.xml', bhs_csl_with_cleaned_tags)
    print('step_2_done')

    # replace Molten's ASCII-based notation with its ISO counterpart
    diacs = get_diacritics('../data/bhs_to_diacs.txt')
    bhs_csl_decoded = decode_diacritics(diacs, '../data/bhs_csl_with_cleaned_tags.xml')
    input_output.print_list(bhs_dir + 'bhs.tei', bhs_csl_decoded)
    print('step_3_done')


bhs_dir = '../../../../c-salt_sanskrit_data/sa_en/bhs/'
process_bhs(bhs_dir)
