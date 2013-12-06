from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.Permissions import webdav_access
from Products.CMFCore.utils import getToolByName
from ftw.caldav.browser.helpers import authenticated
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import ICalendar
from ftw.caldav.interfaces import IDAVReport
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from ftw.caldav.properties.calendars import CalendarsCollectionProperties
from ftw.caldav.utils import event_interface_identifiers
from lxml import etree
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


class CalendarsView(BrowserView):
    implements(IPublishTraverse)

    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    def __init__(self, context, request):
        super(CalendarsView, self).__init__(context, request)
        self.username = None

    def publishTraverse(self, request, name):
        if self.username is None:
            self.username = name
            return self

        elif name in dir(self):
            return getattr(self, name)

        else:
            raise NotFound(self, name)

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
        providers = [CalendarsCollectionProperties(member, self.request)]

        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'object_provides': ICalendar.__identifier__}
        for brain in  catalog(query):
            calendar = brain.getObject()
            providers.append(
                getMultiAdapter((calendar, self.request), ICalDAVProperties))

        generator = getAdapter(self.request, IPROPFINDDocumentGenerator)
        return generator.generate(providers)

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


class CalendarView(BrowserView):
    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    security.declareProtected(webdav_access, 'PROPFIND')
    @authenticated
    def PROPFIND(self, REQUEST, RESPONSE):
        """Retrieve properties of the current user."""
        providers = [getMultiAdapter((self.context, self.request), ICalDAVProperties)]
        generator = getAdapter(self.request, IPROPFINDDocumentGenerator)

        if REQUEST.getHeader('Depth', 'infinity') != '0':
            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'object_provides': event_interface_identifiers(),
                     'path': '/'.join(self.context.getPhysicalPath())}
            for brain in  catalog(query):
                calendar = brain.getObject()
                providers.append(
                    getMultiAdapter((calendar, self.request), ICalDAVProperties))

        return generator.generate(providers)

    security.declarePublic('OPTIONS')
    @authenticated
    def OPTIONS(self, REQUEST, RESPONSE):
        """Retrieve OPTIONS.
        """
        RESPONSE.setHeader('Allow', ', '.join(['PROPFIND', 'OPTIONS', 'REPORT']))
        RESPONSE.setHeader('Content-Length', 0)
        RESPONSE.setHeader('DAV', '1, 2, calendar-access')
        RESPONSE.setStatus(200)
        return RESPONSE

    security.declareProtected(webdav_access, 'REPORT')
    @authenticated
    def REPORT(self, REQUEST, RESPONSE):
        """Retrieve REPORT.
        """
        REQUEST.stdin.seek(0)
        REQUEST.set('BODY', REQUEST.stdin.read())

        report_name = etree.fromstring(REQUEST.get('BODY')).tag
        report = getMultiAdapter((self.context, REQUEST), IDAVReport,
                                 name=report_name)

        response_data = report()
        RESPONSE.setStatus(207)
        RESPONSE.setHeader('Content-Type', 'text/xml; charset="utf-8"')
        RESPONSE.setBody(response_data)
        return RESPONSE
