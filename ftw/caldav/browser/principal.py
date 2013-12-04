from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.Permissions import webdav_access
from Products.CMFCore.utils import getToolByName
from ftw.caldav.browser.helpers import authenticated
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


class PrincipalView(BrowserView):
    implements(IPublishTraverse)

    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    def __init__(self, context, request):
        super(PrincipalView, self).__init__(context, request)
        self.username = None

    def publishTraverse(self, request, name):
        if self.username is None:
            self.username = name
            return self

        elif name in dir(self):
            return getattr(self, name)

        else:
            raise NotFound(name)

    def getMember(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        # Limit access for users to their own principal view for the moment.
        if self.username != member.getId():
            raise Unauthorized()

        return mtool.getMemberById(self.username)

    security.declareProtected(webdav_access, 'PROPFIND')
    @authenticated
    def PROPFIND(self, REQUEST, RESPONSE):
        """Retrieve properties of the current user."""
        member = self.getMember()
        provider = getMultiAdapter((member, self.request), ICalDAVProperties)
        generator = getAdapter(self.request, IPROPFINDDocumentGenerator)
        return generator.generate(provider)
