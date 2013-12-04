from Products.CMFCore.utils import getToolByName
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class TestPropfindRequestOnRoot(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_resourcetype_is_collection(self, browser):
        req_body = propfind.make_propfind_request_body({
                'DAV:': ['resourcetype']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resourcetype'))
        self.assertEquals(['collection'],
                          propfind.property_type('resourcetype'))

    @browsing
    def test_principal_URL(self, browser):
        # http://tools.ietf.org/html/rfc3744#section-4.2
        # This protected property contains the URL that MUST be used to identify
        # this principal in an ACL request.
        req_body = propfind.make_propfind_request_body({
                'DAV:': ['principal-URL']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('principal-URL'))

        self.assertEquals(
            ''.join(('<principal-url xmlns:n="DAV:">',
                     '<href xmlns:n="DAV:">/plone/caldav-principal/test_user_1_</href>',
                     '</principal-url>')),
            propfind.property_xml('principal-URL'))

    @browsing
    def test_current_user_principal(self, browser):
        # http://tools.ietf.org/html/rfc5397#section-3
        req_body = propfind.make_propfind_request_body({
                'DAV:': ['current-user-principal']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('current-user-principal'))

        self.assertEquals(
            ''.join(('<current-user-principal xmlns:n="DAV:">',
                     '<href xmlns:n="DAV:">/plone/caldav-principal/test_user_1_</href>',
                     '</current-user-principal>')),
            propfind.property_xml('current-user-principal'))

    @browsing
    def test_displayname(self, browser):
        # http://tools.ietf.org/html/rfc2518#section-13.2

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['displayname']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('displayname'))
        self.assertEquals('Plone site',
                          propfind.property_value('displayname'))

    @browsing
    def test_supported_report_set_unsupported(self, browser):
        # http://tools.ietf.org/html/rfc3253#section-3.1.5
        # "supported-report-set" (versioning extensions to WebDAV) is currently
        # not supported.

        req_body = propfind.make_propfind_request_body({
                'DAV:': ['supported-report-set']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('supported-report-set'))

    @browsing
    def test_propfind_calendar_home_set_unsupported(self, browser):
        # http://tools.ietf.org/html/rfc4791#section-6.2.1
        # "calendar-home-set" is recommended but optional.
        # We do not have a per-user container for events (yet).

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['calendar-home-set']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-home-set'))

        self.assertEquals(
            ''.join(('<calendar-home-set xmlns:n="urn:ietf:params:xml:ns:caldav">',
                     '<href xmlns:n="DAV:">/plone/caldav-calendars/test_user_1_</href>',
                     '</calendar-home-set>')),
            propfind.property_xml('calendar-home-set'))

    @browsing
    def test_calendar_user_address_set(self, browser):
        # http://tools.ietf.org/html/rfc6638#section-2.4.1
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        member.setMemberProperties({'email': 'test@user.com'})
        transaction.commit()

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['calendar-user-address-set']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-user-address-set'))

        self.assertEquals(
            ''.join(('<calendar-user-address-set'
                     ' xmlns:n="urn:ietf:params:xml:ns:caldav">',
                     '<href xmlns:n="DAV:">mailto:test@user.com</href>',
                     '<href xmlns:n="DAV:">userid:test_user_1_</href>',
                     '<href xmlns:n="DAV:">/plone/caldav-principals/test_user_1_' + \
                         '</href>',
                     '</calendar-user-address-set>')),
            propfind.property_xml('calendar-user-address-set'))

    @browsing
    def test_schedule_inbox_URL_unsupported(self, browser):
        # http://tools.ietf.org/html/rfc6638#section-2.2.1
        # Identify the URL of the scheduling Inbox collection owned
        # by the associated principal resource.
        # Not (yet) implemented.

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['schedule-inbox-URL']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('schedule-inbox-URL'))

    @browsing
    def test_schedule_outbox_URL_unsupported(self, browser):
        # http://tools.ietf.org/html/rfc6638#section-2.1.1
        # Identify the URL of the scheduling Outbox collection owned
        # by the associated principal resource.
        # Not (yet) implemented.

        req_body = propfind.make_propfind_request_body({
                'urn:ietf:params:xml:ns:caldav': ['schedule-outbox-URL']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('schedule-outbox-URL'))

    @browsing
    def test_dropbox_home_URL(self, browser):
        # http://calendarserver.org
        # This is a MacOS extension and is not (yet) supported.

        req_body = propfind.make_propfind_request_body({
                'http://calendarserver.org/ns/': ['dropbox-home-URL']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('dropbox-home-URL'))

    @browsing
    def test_email_address_set(self, browser):
        # http://calendarserver.org
        # This is a MacOS extension and is not (yet) supported.

        req_body = propfind.make_propfind_request_body({
                'http://calendarserver.org/ns/': ['email-address-set']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('email-address-set'))

    @browsing
    def test_notification_URL(self, browser):
        # http://calendarserver.org
        # This is a MacOS extension and is not (yet) supported.

        req_body = propfind.make_propfind_request_body({
                'http://calendarserver.org/ns/': ['notification-URL']})
        browser.login().webdav('PROPFIND', data=req_body)
        self.assertEquals('HTTP/1.1 404 Not Found',
                          propfind.status_for_property('notification-URL'))
