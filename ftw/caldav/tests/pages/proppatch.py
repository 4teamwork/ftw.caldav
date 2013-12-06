from ftw.caldav.interfaces import NAMESPACES
from lxml import etree


def make_proppatch_request_body(namespace, name, value):
    document = etree.Element('{DAV:}propertyupdate', nsmap=NAMESPACES)
    set_ = etree.SubElement(document, '{DAV:}set')
    prop = etree.SubElement(set_, '{DAV:}prop')
    etree.SubElement(prop, '{%s}%s' % (namespace, name)).text = value
    return etree.tostring(document, pretty_print=True)
