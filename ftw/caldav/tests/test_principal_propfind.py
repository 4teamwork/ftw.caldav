from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestPropfindOnPrincipal(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_resourcetype(self, browser):
        # http://tools.ietf.org/html/rfc3744#section-4
        # "PROPFIND" on the principal view must return a DAV:resourcetype
        # of "DAV:principal".

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['resourcetype']})
        browser.login().webdav('PROPFIND', view='caldav-principal/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resourcetype'))
        self.assertEquals('principal',
                          propfind.property_type('resourcetype'))

    @browsing
    def test_displayname(self, browser):
        # http://tools.ietf.org/html/rfc3744#section-4
        # The principal should have a non-empty "displayname" property.

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['displayname']})
        browser.login().webdav('PROPFIND', view='caldav-principal/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('displayname'))
        self.assertEquals(TEST_USER_ID,  # test user has no fullname by default.
                          propfind.property_value('displayname'))

    @browsing
    def test_calendar_home_set(self, browser):
        # http://tools.ietf.org/html/rfc3744#section-4
        # The principal should have a non-empty "displayname" property.

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['calendar-home-set']})
        browser.login().webdav('PROPFIND', view='caldav-principal/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-home-set'))
        self.assertEquals(
            '%s/caldav-calendars/test_user_1_' % self.layer['portal'].portal_url(),
            propfind.property_value('calendar-home-set'))
