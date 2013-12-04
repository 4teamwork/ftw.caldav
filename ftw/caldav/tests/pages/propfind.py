from ftw.testbrowser import browser
from lxml import etree
from zope.component.hooks import getSite


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
    return map(lambda node: node.tag, prop.first.css('>*'))


def property_xml(property_name):
    prop = browser.css(property_name)
    assert len(prop) > 0, 'No property "%s" found in response.' % property_name
    return etree.tostring(prop.first.node)


def propfind_data():
    portal = getSite()
    portal_url = portal.absolute_url()

    data = {}
    for response in browser.css('response'):
        href = response.css('href').first.normalized_text().replace(portal_url, '...')
        data[href] = response_data = {}

        for propstat in response.css('propstat'):
            prop_status = propstat.css('status').first.normalized_text()
            response_data[prop_status] = prop_data = {}

            for property in propstat.css('> prop > *'):
                if len(property.css('>*')) > 0:
                    prop_data[property.tag] = etree.tostring(property.node)
                else:
                    prop_data[property.tag] = property.normalized_text()

    return data


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
