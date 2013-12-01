from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import webdav_access
from zope.publisher.browser import BrowserView


def _traversable(method):
    # Decorator for making webdav methods traversable by setting the __roles__
    # to the default empty string.
    # Otherwise the Zope traversal would not allow to call it.
    method.__roles__ = ''
    return method


class CalendarsView(BrowserView):
    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    def __call__(self):
        return '-- how to use caldav --'

    security.declarePublic('OPTIONS')
    @_traversable
    def OPTIONS(self, REQUEST, RESPONSE):
        """Retrieve communication options."""
        RESPONSE.setHeader('DAV', 'calendar-access')
        self.context.OPTIONS(REQUEST, RESPONSE)
        return RESPONSE

    security.declareProtected(webdav_access, 'PROPFIND')
    @_traversable
    def PROPFIND(self, REQUEST, RESPONSE):
        """Retrieve properties defined on the resource."""
        return self.context.PROPFIND(REQUEST, RESPONSE)


class PloneCalendarsView(CalendarsView):
    pass
