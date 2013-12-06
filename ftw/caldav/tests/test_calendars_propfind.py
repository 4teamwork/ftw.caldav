from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.caldav.tests.pages import propfind
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


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
                       'resourcetype': '<resourcetype><collection/><calendar/>' + \
                           '</resourcetype>'}}},

            propfind.propfind_data())


class TestCalendarProperties(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.calendar = create(
            Builder('calendar')
            .titled(u'First Calendar')
            .having(description=u'The most important calendar.'))

    def propfind(self, browser, namespace, name, headers=None):
        req_body = propfind.make_propfind_request_body({namespace: [name]})
        browser.login().webdav('PROPFIND', self.calendar, view='caldav',
                               data=req_body, headers=headers)

    @browsing
    def test_resourcetype(self, browser):
        self.propfind(browser, 'DAV:', 'resourcetype')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resourcetype'))
        self.assertEquals(['collection', 'calendar'],
                          propfind.property_type('resourcetype'))

    @browsing
    def test_displayname_is_title(self, browser):
        self.propfind(browser, 'DAV:', 'displayname')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('displayname'))
        self.assertEquals('First Calendar',
                          propfind.property_value('displayname'))

    @browsing
    def test_resource_id_is_uid(self, browser):
        self.propfind(browser, 'DAV:', 'resource-id')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('resource-id'))
        self.assertEquals('uuid:%s' % IUUID(self.calendar),
                          propfind.property_value('resource-id'))

    @browsing
    def test_owner(self, browser):
        self.propfind(browser, 'DAV:', 'owner')
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
        self.propfind(browser, 'DAV:', 'getcontenttype')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getcontenttype'))
        self.assertEquals('text/calendar; component=vevent',
                          propfind.property_value('getcontenttype'))

    @browsing
    def test_calendar_description(self, browser):
        self.propfind(browser, 'urn:ietf:params:xml:ns:caldav', 'calendar-description')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('calendar-description'))
        self.assertEquals('The most important calendar.',
                          propfind.property_value('calendar-description'))

    @browsing
    def test_supported_calendar_component_set(self, browser):
        propname = 'supported-calendar-component-set'
        self.propfind(browser, 'urn:ietf:params:xml:ns:caldav', propname)
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property(propname))

        self.assertEquals(
            ''.join(('<supported-calendar-component-set>',
                     '<comp name="VEVENT"/>',
                     '</supported-calendar-component-set>')),
            propfind.property_xml(propname))

    @browsing
    def test_getctag_does_not_change_when_nothing_changed(self, browser):
        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getctag'))
        initial_value = propfind.property_value('getctag')

        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertEquals(initial_value, propfind.property_value('getctag'),
                          'getctag should not have changed!')

    @browsing
    def test_getctag_changes_when_container_changes(self, browser):
        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getctag'))
        initial_value = propfind.property_value('getctag')

        transaction.begin()
        self.calendar.setDescription('A new description')
        notify(ObjectModifiedEvent(self.calendar))
        transaction.commit()

        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertNotEquals(initial_value, propfind.property_value('getctag'),
                             'getctag should have changed on modification but didnt.')

    @browsing
    def test_getctag_changes_when_object_is_added(self, browser):
        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getctag'))
        initial_value = propfind.property_value('getctag')

        transaction.begin()
        create(Builder('event').within(self.calendar))
        transaction.commit()

        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertNotEquals(initial_value, propfind.property_value('getctag'),
                             'getctag should have changed when adding an object.')

    @browsing
    def test_getctag_changes_when_contained_object_changes(self, browser):
        event = create(Builder('event').within(self.calendar))
        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertEquals('HTTP/1.1 200 OK',
                          propfind.status_for_property('getctag'))
        initial_value = propfind.property_value('getctag')

        transaction.begin()
        event.setDescription('A new description')
        notify(ObjectModifiedEvent(event))
        transaction.commit()

        self.propfind(browser, 'http://calendarserver.org/ns/', 'getctag')
        self.assertNotEquals(initial_value, propfind.property_value('getctag'),
                             'getctag should have changed when contained object'
                             'was changed.')

    @browsing
    def test_events_are_listed(self, browser):
        create(Builder('event').titled(u'A Meeting').within(self.calendar))
        self.propfind(browser, 'DAV:', 'displayname')

        self.maxDiff = None
        self.assertEquals(
            {'.../first-calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'First Calendar'}},

             '.../first-calendar/a-meeting/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'A Meeting'}}},

            propfind.propfind_data())

    @browsing
    def test_Depth_header_is_implemented(self, browser):
        create(Builder('event').titled(u'A Meeting').within(self.calendar))
        self.maxDiff = None

        self.propfind(browser, 'DAV:', 'displayname', headers={'Depth': '0'})
        self.assertEquals(
            {'.../first-calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'First Calendar'}}},
            propfind.propfind_data(),
            'Expected no children with request header Depth: 0')

        self.propfind(browser, 'DAV:', 'displayname', headers={'Depth': '1'})
        self.assertEquals(
            {'.../first-calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'First Calendar'}},

             '.../first-calendar/a-meeting/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'A Meeting'}}},

            propfind.propfind_data(),
            'Expected children with request header Depth: 1')

        self.propfind(browser, 'DAV:', 'displayname', headers={'Depth': 'infinity'})
        self.assertEquals(
            {'.../first-calendar/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'First Calendar'}},

             '.../first-calendar/a-meeting/caldav':
                 {'HTTP/1.1 200 OK':
                      {'displayname': 'A Meeting'}}},

            propfind.propfind_data(),
            'Expected children with request header Depth: infinity')
