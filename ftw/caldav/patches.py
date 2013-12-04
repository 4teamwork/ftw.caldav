from OFS.PropertySheets import DAVProperties
from Products.CMFCore.utils import getToolByName


def OPTIONS(self, REQUEST, RESPONSE):
    RESPONSE.setHeader('DAV', 'calendar-access')
    return self._old_OPTIONS(REQUEST, RESPONSE)


def DAVProperties_getProperty(self, id, default=None):
    id = id.replace('-', '_')
    method='dav__%s' % id
    if not hasattr(self, method):
        return default
    return getattr(self, method)()


def dav__current_user_principal(self):
    urltool = getToolByName(self, 'portal_url')
    mtool = getToolByName(self, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    url = '/'.join((urltool(), 'caldav-principal', member.getId()))
    return '<d:href xmlns:n="DAV:">%s</d:href>' % url


DAVProperties.pm = DAVProperties.pm + ({'id': 'current-user-principal', 'mode': 'r',
                                        'meta': {'__xml_attrs__': {}}},)
