from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.interfaces import NAMESPACES
from ftw.caldav.testing import CALDAV_INTEGRATION_TESTING
from ftw.caldav.tests.pages.multiget import make_multiget_request_body
from lxml import etree
from unittest2 import TestCase
from zope.component import getMultiAdapter


REPORT_NAME = '{urn:ietf:params:xml:ns:caldav}calendar-multiget'


class TestCalendarMultigetReport(TestCase):

    layer = CALDAV_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.calendar = create(Builder('calendar').titled(u'Calendar'))

    def test_returns_multistatus_response(self):
        events = (create(Builder('event').titled(u'Meeting').within(self.calendar)),)
        self.request.set('BODY', make_multiget_request_body(events))

        report = getMultiAdapter((self.calendar, self.request), name=REPORT_NAME)
        root = etree.fromstring(report())
        self.assertEquals('{DAV:}multistatus', root.tag)

    def test_returns_report_per_requested_resource(self):
        events = (create(Builder('event').titled(u'Meeting').within(self.calendar)),
                  create(Builder('event').titled(u'Workshop').within(self.calendar)))
        self.request.set('BODY', make_multiget_request_body(events))

        report = getMultiAdapter((self.calendar, self.request), name=REPORT_NAME)
        doc = etree.fromstring(report())
        self.assertEquals(2, len(doc.xpath('//dav:response', namespaces=NAMESPACES)))

    def test_returns_requested_properties(self):
        events = (create(Builder('event').titled(u'Meeting').within(self.calendar)),)
        self.request.set('BODY', make_multiget_request_body(events))

        report = getMultiAdapter((self.calendar, self.request), name=REPORT_NAME)
        doc = etree.fromstring(report())
        self.assertEquals(
            'Meeting',
            doc.xpath('//dav:displayname', namespaces=NAMESPACES)[0].text)
