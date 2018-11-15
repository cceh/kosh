from os import listdir
from os.path import isfile, join, basename
from lxml import etree
import re

NS_TEI = 'http://www.tei-c.org/ns/1.0'
NS_HTML = 'http://www.w3.org/1999/xhtml'

ns = {'tei': 'http://www.tei-c.org/ns/1.0', 'html': NS_HTML}


def apte_csl_into_tei(apte_xml, path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('pg')]

    tree = etree.parse(apte_xml)

    # root = tree.getroot()
    rut = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})
    r = tree.xpath('/ap90')[0]
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
                            h.attrib['type'] = 'standard'
                            h.attrib['ana'] = 'key1'
                            # http://bendustries.org/wp/?p=21
                            h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"
                            # set form id
                            l_n = e.xpath('./tail/L')
                            entry_id = l_n[0].text
                            # print(entry_id)
                            if '.' in entry_id:
                                ## get previous entry
                                print(entry_id)
                                id_splited = entry_id.split('.')
                                previous_form_node = e.getprevious().xpath('./form')[0]
                                print(type(previous_form_node), previous_form_node.tag, len(previous_form_node))
                                # write the altermative written form there
                                alt_orth = etree.Element('orth')
                                alt_orth.attrib['type'] = 'alt'
                                alt_orth.attrib['n'] = id_splited[1].zfill(2)
                                alt_orth.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"
                                alt_orth.text = h.text
                                previous_form_node.append(alt_orth)
                                # delete current element
                                r.remove(e)
                                continue

                            lemma_id = 'lemma_' + h.text + '_' + entry_id
                            # only case here : lemma_arI|a_4072
                            if '|' in lemma_id:
                                lemma_id = lemma_id.replace('|', '')
                            e.attrib['{http://www.w3.org/XML/1998/namespace}id'] = lemma_id
                        if h.tag == 'key2':
                            # remove
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

                        if b.tag == 's':
                            # < hi rendition = "#b" >
                            b.tag = 'hi'
                            b.attrib['rendition'] = '#b'

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
                        if b.tag == 'F':
                            b.tag = 'note'
                            b.attrib['place'] = 'foot'

                        if b.tag == 'P1' or b.tag == 'P':
                            b.tag = 'lb'

                # process tail_info
                if child.tag == 'tail':
                    child.tag = 'note'
                    for t in child:
                        # <idno ana="L" xml:id="ap90_79">79</idno>
                        if t.tag == 'L':
                            t.tag = 'idno'
                            t.attrib['ana'] = 'L'
                            t.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'ap90_' + t.text

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
    title.text = 'The practical Sanskrit-English dictionary, containing appendices on Sanskrit prosody and important literary & geographical names in the ancient history of India, for the use of schools and colleges - V.S. Apte (1890)'

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


def get_all_tags(ap90_tei):
    #tags_pattern = re.compile(r'<(.*?)>')
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(ap90_tei, parser)
    tags_set = set()
    entries = tree.xpath('//tei:entry/tei:sense', namespaces=ns)
    for e in entries:
        e_as_s = etree.tounicode(e)
        # tags = re.findall(tags_pattern, e_as_s)
        # for tag in tags:
        #   tags_set.add(tag)
        e_as_s = re.sub(r'<hi rendition="#b">(.*?)</hi>', r'<b>\1</b>', e_as_s,
                        flags=re.DOTALL)
        e_as_s = re.sub(r'<hi rendition="#i">(.*?)</hi>', r'<i>\1</i>', e_as_s,
                        flags=re.DOTALL)
        e_as_s = re.sub(r'<sense xmlns="http://www.tei-c.org/ns/1.0">(.*?)</sense>', r'<div class="sense">\1</div>',
                        e_as_s,
                        flags=re.DOTALL)
        e_as_s = re.sub(r'<lb/>', r'<br>', e_as_s, flags=re.DOTALL)
        print(e_as_s)

    return tags_set


def transform_ap90_tei(ap90_dir):
    apte_xml = ap90_dir + 'ap90.xml'
    apte_csl_base = apte_csl_into_tei(apte_xml, ap90_dir + 'ap90_pages/')
    apte_csl_base.write(ap90_dir + 'ap90.tei', pretty_print=True, xml_declaration=True, encoding="utf-8")


ap90dir = '../../../../c-salt_sanskrit_data/sa_en/ap90/'
# transform_ap90_tei(ap90dir)


tags_set = get_all_tags(ap90dir + 'ap90.tei')

for tag in tags_set:
    print(tag)
