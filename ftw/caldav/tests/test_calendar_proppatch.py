from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.caldav.tests.pages import proppatch
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestCalendarPROPPATCH(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.calendar = create(Builder('calendar').titled(u'Calendar'))

    def propfind(self, browser, namespace, name):
        req_body = propfind.make_propfind_request_body({namespace: [name]})
        browser.login().webdav('PROPFIND', self.calendar, view='caldav', data=req_body)

    def proppatch(self, browser, namespace, name, value):
        req_body = proppatch.make_proppatch_request_body(namespace, name, value)
        browser.login().webdav('PROPPATCH', self.calendar, view='caldav',
                               data=req_body)

    @browsing
    def test_calendar_color(self, browser):
        self.maxDiff = None
        self.propfind(browser, 'http://apple.com/ns/ical/', 'calendar-color')
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('calendar-color'))

        self.proppatch(browser, 'http://apple.com/ns/ical/', 'calendar-color',
                       '#882F00FF')
        self.assertEquals(
            {'.../calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'calendar-color': ''}}},
            propfind.propfind_data())


        self.propfind(browser, 'http://apple.com/ns/ical/', 'calendar-color')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-color'))
        self.assertEquals('#882F00FF', propfind.property_value('calendar-color'))

    @browsing
    def test_calendar_order(self, browser):
        self.maxDiff = None
        self.propfind(browser, 'http://apple.com/ns/ical/', 'calendar-order')
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('calendar-order'))

        self.proppatch(browser, 'http://apple.com/ns/ical/', 'calendar-order',
                       '3')
        self.assertEquals(
            {'.../calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'calendar-order': ''}}},
            propfind.propfind_data())


        self.propfind(browser, 'http://apple.com/ns/ical/', 'calendar-order')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-order'))
        self.assertEquals('3', propfind.property_value('calendar-order'))
