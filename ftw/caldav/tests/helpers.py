from lxml import etree


def normalize_xml(xmlstring):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.XML(xmlstring, parser=parser)
    return etree.tostring(doc)
