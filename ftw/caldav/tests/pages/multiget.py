from ftw.caldav.interfaces import NAMESPACES
from lxml import etree


def make_multiget_request_body(objects, properties=(('DAV:', 'displayname'), )):
    document = etree.Element('{urn:ietf:params:xml:ns:caldav}calendar-multiget',
                             nsmap=NAMESPACES)
    prop = etree.SubElement(document, '{DAV:}prop')

    for namespace, name in properties:
        etree.SubElement(prop, '{%s}%s' % (namespace, name))

    for obj in objects:
        path = '/'.join(obj.getPhysicalPath() + ('caldav',))
        etree.SubElement(document, '{DAV:}href').text = path

    return etree.tostring(document, pretty_print=True)
