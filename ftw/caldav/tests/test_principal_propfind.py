from Products.CMFCore.utils import getToolByName
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


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
        self.assertEquals(['principal'],
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
            '/plone/caldav-calendars/test_user_1_',
            propfind.property_value('calendar-home-set'))

    @browsing
    def test_calendar_user_address_set(self, browser):
        # http://tools.ietf.org/html/rfc6638#section-2.4.1
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        member.setMemberProperties({'email': 'test@user.com'})
        transaction.commit()

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['calendar-user-address-set']})
        browser.login().webdav('PROPFIND', view='caldav-principal/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-user-address-set'))

        self.assertEquals(
            ''.join(('<calendar-user-address-set>',
                     '<href>mailto:test@user.com</href>',
                     '<href>userid:test_user_1_</href>',
                     '<href>/plone/caldav-principal/test_user_1_</href>',
                     '</calendar-user-address-set>')),
            propfind.property_xml('calendar-user-address-set'))

    @browsing
    def test_current_user_principal(self, browser):
        # http://tools.ietf.org/html/rfc5397#section-3
        req_body = propfind.make_propfind_request_body({
                'DAV:': ['current-user-principal']})
        browser.login().webdav('PROPFIND', view='caldav-principal/test_user_1_',
                               data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('current-user-principal'))
        url = '/plone/caldav-principal/test_user_1_'

        self.assertEquals(
            ''.join(('<current-user-principal>',
                     '<href>%s</href>' % url,
                     '</current-user-principal>')),
            propfind.property_xml('current-user-principal'))
