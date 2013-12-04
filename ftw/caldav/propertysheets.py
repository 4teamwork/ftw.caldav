from OFS.PropertySheets import DAVProperties
from Products.CMFCore.utils import getToolByName


class CalDAVProperties(DAVProperties):

    id = 'caldav'
    _md = {'xmlns': 'urn:ietf:params:xml:ns:caldav'}

    pm = ({'id': 'calendar-home-set', 'mode': 'r',
           'meta': {'__xml_attrs__': {}}},

          {'id': 'calendar-user-address-set', 'mode': 'r',
           'meta': {'__xml_attrs__': {}}},
          )

    def getProperty(self, id, default=None):
        id = id.replace('-', '_')
        return super(CalDAVProperties, self).getProperty(id, default=default)

    def dav__calendar_home_set(self):
        urltool = getToolByName(self, 'portal_url')
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        url = '/'.join((urltool(), 'caldav-calendars', member.getId()))
        return '<d:href xmlns:n="DAV:">%s</d:href>' % url

    def dav__calendar_user_address_set(self):
        urltool = getToolByName(self, 'portal_url')
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if member.getProperty('email'):
            value = 'mailto:%s' % member.getProperty('email')
        else:
            value = '/'.join((urltool(), 'caldav-calendars', member.getId()))

        return '<d:href xmlns:n="DAV:">%s</d:href>' % value
