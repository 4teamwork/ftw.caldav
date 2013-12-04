from OFS.PropertySheets import DAVProperties


def DAVProperties_getProperty(self, id, default=None):
    id = id.replace('-', '_')
    method='dav__%s' % id
    if not hasattr(self, method):
        return default
    return getattr(self, method)()


def dav__current_user_principal(self):
    return '/'.join((self.portal_url(), 'user-calendars'))


DAVProperties.pm = DAVProperties.pm + ({'id': 'current-user-principal', 'mode': 'r'},)
