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
        self.assertEquals(['collection', 'calendar'],
                          propfind.property_type('resourcetype'))

    # @browsing
    # def test_calendars_are_listed(self, browser):
    #     req_body = propfind.make_propfind_request_body({
    #             'DAV:': ['resourcetype']})
