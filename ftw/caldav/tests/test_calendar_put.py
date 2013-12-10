from ftw.builder import Builder
from ftw.builder import create
from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
import transaction


ICAL_DATA = '\n'.join((
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Example Corp.//CalDAV Client//EN',
        'BEGIN:VEVENT',
        'UID:20010712T182145Z-123401@example.com',
        'DTSTAMP:20060712T182145Z',
        'DTSTART:20060714T170000Z',
        'DTEND:20060715T040000Z',
        'SUMMARY:Bastille Day Party',
        'END:VEVENT',
        'END:VCALENDAR',
        ))


class TestCalendarPUT(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.calendar = create(Builder('calendar').titled(u'Calendar'))

    @browsing
    def test_calendar_PUT_creates_event(self, browser):
        browser.login().webdav('PUT', self.calendar, view='caldav/abc123.ics',
                               data=ICAL_DATA,
                               headers={'Content-Type': 'text/calendar'})

        response = browser.response
        self.assertEquals((201, 'Created'), (response.status_code, response.reason))

        transaction.begin()
        self.assertEquals(
            1, len(self.calendar.objectValues()),
            'Expected calendar to contain one object, the created event.')
        event, = self.calendar.objectValues()
        self.assertEquals('"%s"' % IUUID(event), response.headers.get('ETag'))
