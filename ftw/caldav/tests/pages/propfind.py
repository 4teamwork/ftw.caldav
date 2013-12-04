from ftw.testbrowser import browser
from lxml import etree


PROPFIND_REQUEST_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<A:propfind xmlns:A="DAV:">
  <A:prop>
    %s
  </A:prop>
</A:propfind>
'''


def status_for_property(property_name):
    prop = browser.css(property_name)
    assert len(prop) > 0, 'No property "%s" found in response.' % property_name
    return prop.first.parent(css='propstat').css('status').first.normalized_text()


def property_value(property_name):
    prop = browser.css(property_name)
    assert len(prop) > 0, 'No property "%s" found in response.' % property_name
    return prop.first.normalized_text()


def property_type(property_name):
    prop = browser.css(property_name)
    assert len(prop) > 0, 'No property "%s" found in response.' % property_name
    return prop.first.css('>*').first.tag


def property_xml(property_name):
    prop = browser.css(property_name)
    assert len(prop) > 0, 'No property "%s" found in response.' % property_name
    return etree.tostring(prop.first.node)


def make_propfind_request_body(properties):
    lines = []

    if 'DAV:' in properties:
        for propname in properties['DAV:']:
            lines.append('<A:%s/>' % propname)
        del properties['DAV:']

    alphabet = map(chr, range(65, 65+26))
    del alphabet[0]  # start with B, since A is 'DAV:'

    for i, item in enumerate(properties.items()):
        namespace, namespace_properties = item
        prefix = alphabet[i]
        for propname in namespace_properties:
            lines.append(
                '<%(prefix)s:%(propname)s xmlns:%(prefix)s="%(namespace)s"/>' % {
                    'prefix': prefix,
                    'propname': propname,
                    'namespace': namespace})

    return PROPFIND_REQUEST_TEMPLATE % '\n'.join(lines)
