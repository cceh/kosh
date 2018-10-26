from lxml import etree
from os import listdir

from os.path import isfile, join, basename


def stc_into_tei(apte_xml, path_to_pages):
    pages = [join(path_to_pages, f) for f in listdir(path_to_pages) if
             isfile(join(path_to_pages, f)) and f.startswith('stc_pg')]

    tree = etree.parse(apte_xml)

    rut = etree.Element('TEI', attrib={"xmlns": 'http://www.tei-c.org/ns/1.0'})
    r = tree.xpath('/stc')[0]
    r.tag = 'body'

    # modify entries
    for i, e in enumerate(r):
        e.tag = 'entry'
        # rel_lemmata = []
        try:
            rel_lemmata = []
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
                            h.tag = 'hyph'
                            # h.attrib['ana'] = 'key2'
                            # h.attrib['type'] = 'transliterated'
                            h.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-SLP1"

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
                        # it's a rel lemma!
                        if b.tag == 'div' and b.attrib['n'] == 'P':
                            rl = etree.Element('re')
                            # TODO: modify odd (add 'P')
                            rl.attrib['ana'] = 'H3'
                            form_node = etree.SubElement(rl, 'form')
                            orth_node = etree.SubElement(form_node, 'orth')
                            orth_node.attrib['type'] = 'standard'
                            orth_node.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "san-Latn-x-ISO-15919"
                            ital = b.xpath('./i')
                            # the first string in italics should be the rel-lemma
                            rel_lemma = ital[0].text
                            orth_node.text = rel_lemma
                            # remove it from source
                            b.remove(ital[0])
                            sense_node = etree.SubElement(rl, 'sense')
                            for sub_el in b:
                                se = etree.SubElement(sense_node, sub_el.tag)
                                se.text = sub_el.text

                            for sub_el in sense_node:
                                if sub_el.tag == 'i':
                                    sub_el.tag = 'hi'
                                if sub_el.tag == 'lbinfo':
                                    sense_node.remove(sub_el)

                            rel_lemmata.append(rl)
                            child.remove(b)
                            continue
                            # rl.extend(child)
                            # child.append(rl)

                        if b.tag == 'lbinfo':
                            # lbinfo
                            # the prior word has a line break at the Nth character
                            # The lines of the digitization generally represent 'sections' of the text; the
                            # actual line-breaks of the text are not coded.
                            # However, there is markup corresponding to line breaks in the middle of a word.
                            # For instance 'déclinables <lbinfo n="4"/>' indicates that there was a line
                            # break in the word 'déclinables' occurring 4 characters back,
                            # e.g. 'déclina-bles'.
                            # not needed
                            child.remove(b)
                            continue
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
                        # only one footnote in the whole dict
                        if b.tag == 'F':
                            b.tag = 'note'
                            b.attrib['place'] = 'foot'
                        # not consistent difference between paragraph and subpararaph. On the layout is this simply a line break

                        if b.tag == 'P1' or b.tag == 'P':
                            b.tag = 'lb'

                        for c in b:
                            if c.tag == 'lbinfo':
                                # lbinfo
                                # the prior word has a line break at the Nth character
                                # The lines of the digitization generally represent 'sections' of the text; the
                                # actual line-breaks of the text are not coded.
                                # However, there is markup corresponding to line breaks in the middle of a word.
                                # For instance 'déclinables <lbinfo n="4"/>' indicates that there was a line
                                # break in the word 'déclinables' occurring 4 characters back,
                                # e.g. 'déclina-bles'.
                                # not needed
                                b.remove(c)

                # process tail_info
                if child.tag == 'tail':
                    child.tag = 'note'
                    for t in child:
                        # <idno ana="L" xml:id="gra_79">79</idno>

                        if t.tag == 'L':
                            t.tag = 'idno'
                            t.attrib['ana'] = 'L'

                            t.attrib['{http://www.w3.org/XML/1998/namespace}id'] = 'stc_' + t.text

                        # <tail><L>79</L><pc>0008</pc></tail>
                        if t.tag == 'pc':
                            t.tag = 'ref'
                            t.attrib['type'] = 'facs'

                            # in the xml file facsimilies are referenced (page,column), which is not actually needed

                            original_page_ref = t.text
                            original_page_ref = original_page_ref.split(',')
                            new_page_ref = original_page_ref[0].zfill(3)

                            for col in pages:
                                if new_page_ref in str(col):
                                    print(new_page_ref)
                                    t.attrib['target'] = col.replace(path_to_pages, '#')

                for re in rel_lemmata:
                    e.append(re)




        except TypeError as err:
            print(err)

    # add header info
    header = etree.Element("teiHeader")
    file_desc = etree.SubElement(header, 'fileDesc')

    title_stmt = etree.SubElement(file_desc, 'titleStmt')
    title = etree.SubElement(title_stmt, 'title')
    title.text = 'Stchoupak Dictionnaire Sanscrit-Français - Stchoupak, Nadine (1959)'

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


def transform_stc():
    apte_xml = 'data/stc.xml'
    stc_base = stc_into_tei(apte_xml, 'data/images/')
    stc_base.write('data/stc.tei', pretty_print=True, xml_declaration=True, encoding="utf-8")


transform_stc()
