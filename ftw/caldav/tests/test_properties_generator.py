from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from ftw.caldav.testing import CALDAV_INTEGRATION_TESTING
from ftw.caldav.tests.helpers import normalize_xml
from lxml import etree
from unittest2 import TestCase
from zope.component import getAdapter
from zope.component import queryAdapter
from zope.interface.verify import verifyObject


PROPFIND_DISPLAYNAME = '<dav:displayname>Example Object</dav:displayname>'
PROPFIND_RESOURCETYPE = ''.join((
        '<dav:resourcetype>',
        '    <dav:collection/>',
        '    <cal:calendar/>',
        '</dav:resourcetype>',
        ))

PROPFIND_RESPONSE_TEMPLATE = ''.join((
        '<dav:multistatus xmlns:cs="http://calendarserver.org/ns/" ',
        '                 xmlns:dav="DAV:" ',
        '                 xmlns:cal="urn:ietf:params:xml:ns:caldav">',
        '    <dav:response>',
        '        <dav:href>http://nohost/plone/example</dav:href>',
        '        <dav:propstat>',
        '            <dav:prop>',
        '%s',
        '            </dav:prop>',
        '            <dav:status>HTTP/1.1 200 OK</dav:status>',
        '        </dav:propstat>',
        '    </dav:response>',
        '</dav:multistatus>',
        ))


class ExampleProperties(CalDAVPropertiesAdapter):

    def get_href(self):
        return 'http://nohost/plone/example'

    @caldav_property('displayname', 'DAV:')
    def displayname(self):
        return 'Example Object'

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        etree.SubElement(parent_node, '{DAV:}collection')
        etree.SubElement(parent_node, '{urn:ietf:params:xml:ns:caldav}calendar')


class TestPROPFINDDocumentGenerator(TestCase):

    layer = CALDAV_INTEGRATION_TESTING

    def test_adapter_is_registered(self):
        portal = self.layer['portal']
        self.assertTrue(queryAdapter((portal, None), IPROPFINDDocumentGenerator),
                        'Default IPROPFINDDocumentGenerator adapter is not registerd.')

    def test_adapter_implements_interface(self):
        adapter = getAdapter(None, IPROPFINDDocumentGenerator)
        verifyObject(IPROPFINDDocumentGenerator, adapter)

    def test_create_document(self):
        adapter = getAdapter(None, IPROPFINDDocumentGenerator)
        self.assertEquals(etree._Element, type(adapter.create_document()))

    def test_add_properties(self):
        adapter = getAdapter(None, IPROPFINDDocumentGenerator)
        document = adapter.create_document()

        provider = ExampleProperties(None, None)
        adapter.add_response(document, provider)

        self.assertEquals(
            normalize_xml(PROPFIND_RESPONSE_TEMPLATE % (
                    ''.join((PROPFIND_DISPLAYNAME, PROPFIND_RESOURCETYPE)))),
            normalize_xml(etree.tostring(document)))

    def test_generate_single_property(self):
        request_data = ''.join((
                '<d:propfind xmlns:d="DAV:">',
                '  <d:prop>',
                '     <d:displayname />',
                '  </d:prop>',
                '</d:propfind>'))

        request = self.layer['request']
        request.set('BODY', request_data)

        provider = ExampleProperties(None, None)
        adapter = getAdapter(self.layer['request'], IPROPFINDDocumentGenerator)
        adapter.generate([provider])

        self.assertEquals(207, request.RESPONSE.getStatus())
        self.assertEquals(
            normalize_xml(PROPFIND_RESPONSE_TEMPLATE % PROPFIND_DISPLAYNAME),
            normalize_xml(request.RESPONSE.body))

    def test_generate_all_properties(self):
        request_data = ''.join((
                '<d:propfind xmlns:d="DAV:">',
                '  <d:allprop/>',
                '</d:propfind>'))

        request = self.layer['request']
        request.set('BODY', request_data)

        provider = ExampleProperties(None, None)
        adapter = getAdapter(self.layer['request'], IPROPFINDDocumentGenerator)
        adapter.generate([provider])

        self.assertEquals(207, request.RESPONSE.getStatus())
        self.assertEquals(
            normalize_xml(PROPFIND_RESPONSE_TEMPLATE % ''.join((
                        PROPFIND_DISPLAYNAME, PROPFIND_RESOURCETYPE))),
            normalize_xml(request.RESPONSE.body))

    def test_generate_list_names(self):
        request_data = ''.join((
                '<d:propfind xmlns:d="DAV:">',
                '  <d:propname/>',
                '</d:propfind>'))

        request = self.layer['request']
        request.set('BODY', request_data)

        provider = ExampleProperties(None, None)
        adapter = getAdapter(self.layer['request'], IPROPFINDDocumentGenerator)
        adapter.generate([provider])

        self.assertEquals(207, request.RESPONSE.getStatus())
        self.assertEquals(
            normalize_xml(PROPFIND_RESPONSE_TEMPLATE % ''.join((
                        '<dav:displayname/>',
                        '<dav:resourcetype/>'))),
            normalize_xml(request.RESPONSE.body))
