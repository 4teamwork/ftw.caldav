from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
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
        browser.login().webdav('PROPFIND', view='caldav-principal', data=req_body)
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
        browser.login().webdav('PROPFIND', view='caldav-principal', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('displayname'))
        self.assertEquals('Test User',
                          propfind.property_value('displayname'))
