import re
from os import listdir
from os.path import basename
from os.path import isfile, join
import string

translator = str.maketrans('', '', string.punctuation)

from lxml import etree

from utils import input_output


def vei_csl_into_tei(vei_xml, path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('pg')]

    tree = etree.parse(vei_xml)

    # root = tree.getroot()
    rut = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})
    r = tree.xpath('/vei')[0]
    r.tag = 'body'

    # modify entries
    for i, e in enumerate(r):
        # H1 -> entry
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
                            ## '|' can't be used as xml_id. Entries 1874 (purumI|a) and 3618 (sumI|a) are now 'purumI-a' and 'sumI-a'
                            if '|' in h.text:
                                h.text = h.text.replace('|', '-')
                            # set form id
                            l_n = e.xpath('./tail/L')
                            e.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'lemma_' + h.text + '_' + l_n[
                                0].text
                        if h.tag == 'key2':
                            h.tag = 'orth'
                            h.attrib['type'] = 'standard'
                            h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-ISO-15919"
                            vei_lemma = h.text
                            vei_lemma = vei_lemma.translate(translator)
                            vei_lemma = vei_lemma.lower()
                            h.text = vei_lemma

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

                        # notes
                        if b.tag == 'F':
                            b.tag = 'note'
                            b.attrib['place'] = 'end'
                            # b.attrib['type'] = 'reference'

                            for c in b:
                                if c.tag == 'i':
                                    # < hi rendition = "#i" >
                                    c.tag = 'hi'
                                    c.attrib['rendition'] = '#i'
                                if c.tag == 'b':
                                    # < hi rendition = "#i" >
                                    c.tag = 'hi'
                                    c.attrib['rendition'] = '#b'
                                if c.tag == 'br' or c.tag == '':
                                    c.tag = 'lb'
                                for sub in c:
                                    if sub.tag == 'br' or sub.tag == '':
                                        sub.tag = 'lb'

                        # not consistent difference between paragraph and subpararaph. On the layout is this simply a line break

                        if b.tag == 'P1' or b.tag == 'P' or b.tag == 'br' or b.tag == '':
                            b.tag = 'lb'
                            # dirty solution
                        if b.tag == 'C1' or b.tag == 'C2' or b.tag == 'C3':
                            b.tag = 'lb'

                # process tail_info
                if child.tag == 'tail':
                    child.tag = 'note'
                    for t in child:
                        # <idno ana="L" xml:id="vei_79">79</idno>
                        if t.tag == 'L':
                            t.tag = 'idno'
                            t.attrib['ana'] = 'L'
                            t.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'vei_' + t.text

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
    title.text = 'Vedic Index of Names and Subjects - Macdonell & Keith (1912)'

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


def replace_diacritics(diacritics, grassman_tei):
    vei = input_output.file_to_list(grassman_tei)
    processed = []

    for line in vei:
        # we split every line
        line = line.split()
        # process every string
        for i, s in enumerate(line):

            for d in diacritics:
                # if diac in string
                p = re.compile(d + r'(?!\d+|>|")')
                matchObject = re.search(p, s)

                if matchObject:
                    # replace it
                    s = s.replace(d, diacritics.get(d))
                    line[i] = s

            line[i] = s

        processed.append(" ".join(line))

    return processed


def add_centered_tags(vei_tei):
    with open(vei_tei, 'r') as file:
        data = file.read()
        data = re.sub(r'<H/>(.*?)<lb/>', r'<lb/><hi rendition="#center">\1</hi><lb/>', data);
        data = re.sub(r'<H/>(.*?)</sense>', r'<lb/><hi rendition="#center">\1</hi></sense>', data);
        data = re.sub(r'§§<lb/>', r'<lb/>   ', data);

    return data


def get_diacritics(path_to_diacritics):
    with open(path_to_diacritics, mode='r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        d = {}
        for l in lines:
            l = l.split()
            d[l[0]] = l[3]

    return d


def transform_vei_tei(vei_dir):
    vei_xml = vei_dir + 'vei.xml'
    vei_xml_tei = 'data/vei_tei_1.xml'
    root = vei_csl_into_tei(vei_xml, vei_dir + 'vei_pages')
    root.write(vei_xml_tei, pretty_print=True, xml_declaration=True, encoding="utf-8")

    data = add_centered_tags(vei_xml_tei)
    input_output.to_file('data/vei_tei_2.xml', data)
    vei_with_diacs = 'data/vei_tei_2.xml'

    d = get_diacritics('data/vei_to_replace.txt')
    vei_without_diacs = replace_diacritics(d, vei_with_diacs)
    input_output.print_list(vei_dir + 'vei.tei', vei_without_diacs)


#vei_dir = '../../../c-salt_sanskrit_data/sa_en/vei/'
#transform_vei_tei(vei_dir)
