from Products.CMFCore.utils import getToolByName
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.testing import CALDAV_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter


class TestUserPropertiesAdapter(TestCase):

    layer = CALDAV_INTEGRATION_TESTING

    def get_member(self):
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        return mtool.getMemberById(TEST_USER_ID)

    def get_adapter(self):
        return getMultiAdapter((self.get_member(), None), ICalDAVProperties)

    def test_adapter_is_registered(self):
        adapter = queryMultiAdapter((self.get_member(), None), ICalDAVProperties)
        self.assertTrue(adapter, 'Could not find ICalDAVProperties adapter for user.')

    def test_displayname_property_is_fullname(self):
        self.get_member().setMemberProperties({'fullname': 'Test User'})
        adapter = self.get_adapter()
        self.assertEquals([{'name': 'displayname',
                            'namespace': 'DAV:',
                            'status_code': 200,
                            'value': 'Test User'}],

                          adapter.get_properties(['displayname']))

    def test_displayname_property_falls_back_to_userid(self):
        self.get_member().setMemberProperties({'fullname': ''})
        adapter = self.get_adapter()
        self.assertEquals([{'name': 'displayname',
                            'namespace': 'DAV:',
                            'status_code': 200,
                            'value': TEST_USER_ID}],

                          adapter.get_properties(['displayname']))

    def test_calendar_home_set(self):
        adapter = self.get_adapter()
        self.assertEquals(
            [{'name': 'calendar-home-set',
              'namespace': 'urn:ietf:params:xml:ns:caldav',
              'status_code': 200,
              'value': 'http://nohost/plone/caldav-calendars/%s' % TEST_USER_ID}],

            adapter.get_properties(['calendar-home-set']))
