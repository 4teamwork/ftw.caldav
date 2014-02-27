from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
import re


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

    @browsing
    def test_getetag_returns_uuid_as_quoted_string(self, browser):
        event = create(Builder('event'))
        self.propfind(browser, event, 'DAV:', 'getetag')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getetag'))
        self.assertEquals('"%s"' % IUUID(event),
                          propfind.property_value('getetag'))

    @browsing
    def test_calendar_data(self, browser):
        event = create(Builder('event')
                       .titled(u'Carnival in Bern')
                       .having(location=u'Bern')
                       .starting(datetime(2014, 4, 6, 05, 00))
                       .ending(datetime(2014, 4, 8, 12, 00)))

        self.propfind(browser, event, 'urn:ietf:params:xml:ns:caldav', 'calendar-data')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-data'))

        expected = ''.join((
                'BEGIN:VCALENDAR VERSION:2.0'
                ' PRODID:-//Plone.org//NONSGML plone.app.event//EN'
                ' X-WR-CALNAME:Carnival in Bern'
                ' X-WR-RELCALID:%(uuid)s'
                ' X-WR-TIMEZONE:Europe/Vienna '
                'BEGIN:VEVENT'
                ' SUMMARY:Carnival in Bern'
                ' DTSTART;TZID=Etc/Greenwich;VALUE=DATE-TIME:20140406T050000'
                ' DTEND;TZID=Etc/Greenwich;VALUE=DATE-TIME:20140408T120000'
#                ' DTSTAMP;VALUE=DATE-TIME:20131206T093327Z'
                ' UID:%(uuid)s'
#                ' CREATED;VALUE=DATE-TIME:%(created)s'
#                ' LAST-MODIFIED;VALUE=DATE-TIME:%(last-modified)s'
                ' LOCATION:Bern'
                ' URL:%(url)s '
                'END:VEVENT '
                'END:VCALENDAR')) % {

            'uuid': IUUID(event),
            'url': event.absolute_url()}

        got = propfind.property_value('calendar-data')

        # Remove all times / dates which are changing and are not precisely predictable
        got = re.sub(r' DTSTAMP;[^ ]*? ', ' ', got)
        got = re.sub(r' CREATED;[^ ]*? ', ' ', got)
        got = re.sub(r' LAST-MODIFIED;[^ ]*? ', ' ', got)

        self.assertEquals(expected, got)
