from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase


class TestEventPropfind(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    def propfind(self, browser, obj, namespace, name):
        req_body = propfind.make_propfind_request_body({namespace: [name]})
        browser.login().webdav('PROPFIND', obj, view='caldav',
                               data=req_body)

    @browsing
    def test_displayname_is_title(self, browser):
        event = create(Builder('event').titled(u'A meeting'))
        self.propfind(browser, event, 'DAV:', 'displayname')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('displayname'))
        self.assertEquals('A meeting',
                          propfind.property_value('displayname'))

    @browsing
    def test_resource_id_is_uid(self, browser):
        event = create(Builder('event'))
        self.propfind(browser, event, 'DAV:', 'resource-id')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resource-id'))
        self.assertEquals('uuid:%s' % IUUID(event),
                          propfind.property_value('resource-id'))

    @browsing
    def test_owner(self, browser):
        event = create(Builder('event'))
        self.propfind(browser, event, 'DAV:', 'owner')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('owner'))

        url = '%s/caldav-principal/test_user_1_' % self.layer['portal'].portal_url()
        self.assertEquals(
            ''.join(('<owner>',
                     '<href>%s</href>' % url,
                     '</owner>')),
            propfind.property_xml('owner'))

    @browsing
    def test_getcontenttype(self, browser):
        event = create(Builder('event'))
        self.propfind(browser, event, 'DAV:', 'getcontenttype')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getcontenttype'))
        self.assertEquals('text/calendar; component=vevent',
                          propfind.property_value('getcontenttype'))

    # @browsing
    # def test_getetag_returns_uuid_as_quoted_string(self, browser):
    #     event = create(Builder('event'))
    #     self.propfind(browser, event, 'DAV:', 'getetag')
    #     self.assertEquals('HTTP/1.1 200 OK',
    #                       propfind.status_for_property('getetag'))
    #     self.assertEquals('"%s"' % IUUID(event),
    #                       propfind.property_value('getetag'))
