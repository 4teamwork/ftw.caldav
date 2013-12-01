from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestOptionsRequestOnCaldavView(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_dav_calendar_access_option_promoted(self, browser):
        browser.webdav('OPTIONS', view='calendars')
        self.assertEquals('calendar-access, 1,2',
                          browser.response.headers.get('DAV'),
                          '"DAV" option does not provide calendar-access correctly.')
