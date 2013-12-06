from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import multiget
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestCalendarsMultigetReport(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.calendar = create(Builder('calendar').titled(u'Calendar'))

    def multiget(self, browser, objects, properties=(('DAV:', 'displayname'),)):
        req_body = multiget.make_multiget_request_body(objects, properties=properties)
        browser.login().webdav('REPORT', self.calendar, view='caldav',
                               data=req_body)

    @browsing
    def test_multiget_returns_properties_of_multiple_resources(self, browser):
        self.maxDiff = None
        events = (create(Builder('event').titled(u'Meeting').within(self.calendar)),
                  create(Builder('event').titled(u'Workshop').within(self.calendar)))
        self.multiget(browser, events)

        self.assertEquals(
            {'.../calendar/meeting/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'Meeting'}},

             '.../calendar/workshop/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'Workshop'}}},

            propfind.propfind_data())
