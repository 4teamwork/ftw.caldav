from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestPropfindOnPrincipal(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_resourcetype(self, browser):
        # http://tools.ietf.org/html/rfc4791#section-4.2

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['resourcetype']})
        browser.login().webdav('PROPFIND', view='caldav-calendars/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resourcetype'))
        self.assertEquals(['collection'],
                          propfind.property_type('resourcetype'))

    @browsing
    def test_calendars_are_listed(self, browser):
        create(Builder('calendar')
               .titled(u'First Calendar'))

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['resourcetype', 'displayname']})
        browser.login().webdav('PROPFIND', view='caldav-calendars/test_user_1_',
                               data=req_body)

        self.maxDiff = None
        self.assertEquals(
            {'.../caldav-calendars/test_user_1_':
                 {'HTTP/1.1 200 OK':
                      {'resourcetype': '<resourcetype><collection/></resourcetype>'},
                  'HTTP/1.1 404 Not Found':
                      {'displayname': ''}},

             '.../first-calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'First Calendar',
                       'resourcetype': '<resourcetype><calendar/></resourcetype>'}}},

            propfind.propfind_data())
