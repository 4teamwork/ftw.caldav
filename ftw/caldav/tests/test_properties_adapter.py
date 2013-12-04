from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from lxml import etree
from unittest2 import TestCase


class ExampleProperties(CalDAVPropertiesAdapter):

    @caldav_property('displayname', 'DAV:')
    def displayname(self):
        return 'Foo'

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        etree.SubElement(parent_node, '{DAV:}collection')
        etree.SubElement(parent_node, '{urn:ietf:params:xml:ns:caldav}calendar')


class TestCalDAVPropertiesAdapter(TestCase):

    def test_get_simple_properties(self):
        self.assertEquals(
            [{'name': 'displayname',
              'namespace': 'DAV:',
              'status_code': 200,
              'value': 'Foo'}],

             ExampleProperties(None, None).get_properties(['displayname']))

    def test_get_callback_properties(self):
        adapter = ExampleProperties(None, None)
        result = adapter.get_properties(['resourcetype'])
        self.assertEquals(
            [{'name': 'resourcetype',
              'namespace': 'DAV:',
              'status_code': 200,
              'callback': adapter.resourcetype}],

            result)

        callback = result[0]['callback']
        prop = etree.Element('{DAV:}resourcetype', nsmap={
                'dav': 'DAV:',
                'cal': 'urn:ietf:params:xml:ns:caldav'})
        callback(prop)

        self.assertEquals(
            '<dav:resourcetype xmlns:dav="DAV:"'
            ' xmlns:cal="urn:ietf:params:xml:ns:caldav">'
            '<dav:collection/>'
            '<cal:calendar/>'
            '</dav:resourcetype>',
            etree.tostring(prop))
