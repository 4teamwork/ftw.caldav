from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import webdav_access
from ftw.caldav.browser.helpers import authenticated
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView


class EventView(BrowserView):
    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    security.declareProtected(webdav_access, 'PROPFIND')
    @authenticated
    def PROPFIND(self, REQUEST, RESPONSE):
        """Retrieve properties of the current user."""
        provider = getMultiAdapter((self.context, self.request), ICalDAVProperties)
        generator = getAdapter(self.request, IPROPFINDDocumentGenerator)
        return generator.generate([provider])

    security.declarePublic('OPTIONS')
    @authenticated
    def OPTIONS(self, REQUEST, RESPONSE):
        """Retrieve OPTIONS.
        """
        RESPONSE.setHeader('Allow', ', '.join(['PROPFIND', 'OPTIONS']))
        RESPONSE.setHeader('Content-Length', 0)
        RESPONSE.setHeader('DAV', '1, 2, calendar-access')
        RESPONSE.setStatus(200)
        return RESPONSE
