from collections import defaultdict
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import NAMESPACES
from ftw.caldav.utils import parse_proppatch_request
from lxml import etree
from zope.component import getMultiAdapter
from zope.publisher.interfaces import NotFound
import httplib


def PROPPATCH(context, REQUEST, RESPONSE, provider=None):
    properties = parse_proppatch_request(REQUEST.get('BODY'))
    if not provider:
        provider = getMultiAdapter((context, REQUEST), ICalDAVProperties)

    result = defaultdict(list)
    for namespace, name, value in properties:
        try:
            provider.set_property(namespace, name, value)
        except NotFound:
            result[404].append((namespace, name))
        else:
            result[200].append((namespace, name))

    document = etree.Element('{DAV:}multistatus', nsmap=NAMESPACES)
    response = etree.SubElement(document, '{DAV:}response')
    etree.SubElement(response, '{DAV:}href').text = provider.get_href()

    for code, props in result.items():
        propstat = etree.SubElement(response, '{DAV:}propstat')
        prop = etree.SubElement(propstat, '{DAV:}prop')

        for namespace, name in props:
            etree.SubElement(prop, '{%s}%s' % (namespace, name))


        etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 %s %s' % (
            code, httplib.responses[code])

    response_data = etree.tostring(document, pretty_print=True)
    RESPONSE.setStatus(207)
    RESPONSE.setHeader('Content-Type', 'text/xml; charset="utf-8"')
    RESPONSE.setBody(response_data)
    return RESPONSE
