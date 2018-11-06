import re
from unicodedata import name

from lxml import etree


def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
             list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
             [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))


def test_regex(to_test):
    with open(to_test, mode='r') as file:
        data = file.read()
        # print(data)
        regex = r'<H/>(.*?)<lb/>'
        if re.search(regex, data, re.DOTALL):
            matches = re.findall(regex, data, flags=re.DOTALL)
            # print(matches)
            # print(len(matches))
            # for match in matches:
            #    print(match)
            # data = re.sub(r'<H/>(.*?)<lb/>', r'<lb/><hi rendition="#center">\1</hi><lb/>', data);
            # data = re.sub(r'§§<lb/>', r'<lb/>   ', data);

        data = re.sub(r'<H/>', r'<lb/><H/>', data, flags=re.DOTALL)
        data = re.sub(r'§§<lb/>', r'<lb/>   ', data, flags=re.DOTALL)
        data = re.sub(r'<H/>(.*?)<lb/>', r'<lb/><hi rendition="#center">\1</hi><lb/>', data, flags=re.DOTALL)
        data = re.sub(r'<H/>(.*?)</sense>', r'<lb/><hi rendition="#center">\1</hi><lb/></sense>', data, flags=re.DOTALL)


        # data = re.sub(r'<H/>(.*?)<lb/>', r'<lb/><hi rendition="#center">\1</hi><lb/>', data, flags=re.DOTALL)

    return data


def test_xpath(to_test):
    tree = etree.parse(to_test)
    r = tree.xpath('/TEI/text/body/entry/sense/*')
    # check all tags ins 'sense'
    for e in r:
        # if there is an '<H/>'
        if e.tag == 'H':
            # check the siblings
            for t in e.xpath('./following-sibling::*'):
                # if there is an '<H/>'
                if t.tag == 'H':
                    print(e.xpath('../../@xml:id'))
                    #    print(e.getparent().getparent().attrib['{http://www.w3.org/XML/1998/namespace}id'])


def flat_them_all(to_test):
    tree = etree.parse(to_test)
    senses = tree.xpath('/TEI/text/body/entry/sense/*')

    # counter = 0
    for i, e in enumerate(senses):
        result = stringify_children(e)
        print(result)


def test_iterator(to_test):
    result = []
    tree = etree.parse(to_test)
    for v in tree.getiterator("sense"):
        print(v.text)
    return len(result)


def test_unicode_literal():
    e = "\u1e6dÄB"
    print(e, type(e))


def test_print_unicode_char_name(s):
    for e in s:
        print(e, name(e))




