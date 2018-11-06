from lxml import etree

NS_TEI = 'http://www.tei-c.org/ns/1.0'
NS_HTML = 'http://www.w3.org/1999/xhtml'

ns = {'tei': 'http://www.tei-c.org/ns/1.0', 'html': NS_HTML}


def create_tei_file(entries, slice_number):
    slice_number += 1
    rut = etree.Element('TEI', nsmap={None: NS_TEI})

    # add header info
    header = etree.Element("teiHeader")
    file_desc = etree.SubElement(header, 'fileDesc')

    title_stmt = etree.SubElement(file_desc, 'titleStmt')
    title = etree.SubElement(title_stmt, 'title')
    title.text = 'Monier-Williams Sanskrit-English Dictionary' + '_' + str(slice_number)

    publication_stmt = etree.SubElement(file_desc, 'publicationStmt')
    p_publisher = etree.SubElement(publication_stmt, 'p')
    p_publisher.text = 'CCeH - Cologne Center for eHumanities - 2018'

    source_desc = etree.SubElement(file_desc, 'sourceDesc')
    p_source_desc = etree.SubElement(source_desc, 'p')
    p_source_desc.text = 'TEI file - Lazarus Project'

    # text
    text = etree.Element("text")
    body = etree.SubElement(text, 'body')

    # add entries
    for i, e in enumerate(entries):
        body.append(e)

    rut.append(header)
    rut.append(text)

    et = etree.ElementTree(rut)

    return et


def split_mw72(mw72_dir):
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(mw72_dir + 'mw72.tei', parser)
    # entries = tree.xpath('/ns:TEI/ns:text/ns:body/ns:div/ns:entry', namespaces=namespaces)
    entries = tree.xpath('//tei:entry', namespaces=ns)
    chunks = [entries[x:x + 1000] for x in range(0, len(entries), 1000)]
    for i, chunk in enumerate(chunks):
        i += 1
        et = create_tei_file(chunk, i)
        et.write(mw72_dir + '/splitted/' + 'mw72_{}.tei'.format(str(i).zfill(2)), pretty_print=True,
                 xml_declaration=True, encoding="utf-8")


def get_all_entries(mw72_tei):
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(mw72_tei, parser)
    entries = tree.xpath('.//tei:entry', namespaces=ns)
    # entries = tree.findall('.//entry')
    print(etree.tostring(entries[0]))


mw72_dir = '../../../../c-salt_sanskrit_data/sa_en/mw72/'
# mw72_tei = mw72_dir + 'mw72.tei'

split_mw72(mw72_dir)
# get_all_entries(mw72_tei)
