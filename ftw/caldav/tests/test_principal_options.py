from ftw.caldav.testing import CALDAV_ZSERVER_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestPropfindOnPrincipal(TestCase):

    layer = CALDAV_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_dav_calendar_access_option_promoted(self, browser):
        browser.login().webdav('OPTIONS', view='caldav-principal/test_user_1_')
        self.assertEquals('1, 2, calendar-access',
                          browser.response.headers.get('DAV'),
                          '"DAV" option does not provide calendar-access correctly.')
