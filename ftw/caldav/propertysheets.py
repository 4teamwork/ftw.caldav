from OFS.PropertySheets import DAVProperties
from Products.CMFCore.utils import getToolByName
from ftw.caldav.utils import portal_url_prefix


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
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        url = '/'.join((portal_url_prefix(), 'caldav-calendars', member.getId()))
        return '<d:href xmlns:n="DAV:">%s</d:href>' % url

    def dav__calendar_user_address_set(self):
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        result = []
        href = '<d:href xmlns:n="DAV:">%s</d:href>'

        if member.getProperty('email'):
            result.append(href % 'mailto:%s' % member.getProperty('email'))

        result.append(href % 'userid:%s' % member.getId())
        result.append(href % '/'.join(
                (portal_url_prefix(), 'caldav-principals', member.getId())))

        portal_url = getToolByName(self, 'portal_url')
        result.append(href % '/'.join(
                (portal_url(), 'caldav-principals', member.getId())))

        return ''.join(result)
