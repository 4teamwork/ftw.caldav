from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import webdav_access
from ftw.caldav.browser.helpers import _traversable
from zope.publisher.browser import BrowserView


class PrincipalView(BrowserView):
    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    security.declareProtected(webdav_access, 'PROPFIND')
    @_traversable
    def PROPFIND(self, REQUEST, RESPONSE):
        """Retrieve properties defined on the resource."""
        return self.context.PROPFIND(REQUEST, RESPONSE)
