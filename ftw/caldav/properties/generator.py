from collections import defaultdict
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from ftw.caldav.interfaces import NAMESPACES
from ftw.caldav.interfaces import PROP_PROPNAMES
from ftw.caldav.utils import parse_property_request
from lxml import etree
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
import httplib


def group_properties_by_status_code(properties):
    result = defaultdict(list)
    for property in properties:
        result[property['status_code']].append(property)
    return result


class PROPFINDDocumentGenerator(object):
    implements(IPROPFINDDocumentGenerator)
    adapts(Interface)

    def __init__(self, request):
        self.request = request

    def create_document(self):
        return etree.Element('{DAV:}multistatus', nsmap=NAMESPACES)

    def add_response(self, document, properties_provider, select_properties=None,
                     names_only=False):
        response = etree.SubElement(document, '{DAV:}response')
        etree.SubElement(response, '{DAV:}href').text = properties_provider.get_href()

        if select_properties is None:
            property_names = None
        else:
            property_names = [prop[0] for prop in select_properties]
        self._add_properties_by_statuscode(
            response,
            properties_provider.get_properties(property_names, names_only=names_only),
            select_properties)

    def _add_properties_by_statuscode(self, response, properties,
                                      requested_properties):
        if requested_properties is not None:
            missing_properties = requested_properties[:]
        else:
            missing_properties = []

        properties_by_code = group_properties_by_status_code(properties)

        for code, properties in properties_by_code.items():
            propstat = etree.SubElement(response, '{DAV:}propstat')
            prop = etree.SubElement(propstat, '{DAV:}prop')

            for property in properties:
                prop_node = etree.SubElement(prop, '{%s}%s' % (
                        property['namespace'], property['name']))

                if 'callback' in property:
                    property['callback'](prop_node)
                elif 'value' in property:
                    value = property['value']
                    if isinstance(value, str):
                        prop_node.text = value.decode('utf-8')
                    else:
                        prop_node.text = unicode(value)

                if (property['name'], property['namespace']) in missing_properties:
                    missing_properties.remove(
                        (property['name'], property['namespace']))

            etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 %s %s' % (
                code, httplib.responses[code])

        if not missing_properties:
            return

        propstat = etree.SubElement(response, '{DAV:}propstat')
        prop = etree.SubElement(propstat, '{DAV:}prop')
        for property_name, property_namespace in missing_properties:
            etree.SubElement(prop, '{%s}%s' % (property_namespace, property_name))

        etree.SubElement(propstat, '{DAV:}status').text = 'HTTP/1.1 %s %s' % (
            '404', httplib.responses[404])

    def generate(self, property_providers, subobjects=None):
        names_only = False
        prop_mode, properties = parse_property_request(self.request.get('BODY'))

        if prop_mode == PROP_PROPNAMES:
            names_only = True

        document = self.create_document()
        for provider in property_providers:
            self.add_response(document,
                              provider,
                              select_properties=properties,
                              names_only=names_only)

        response = self.request.RESPONSE
        response.setStatus(207)
        response.setHeader('Content-Type', 'text/xml; charset="utf-8"')
        response.setBody(etree.tostring(document, pretty_print=True))
        return response
