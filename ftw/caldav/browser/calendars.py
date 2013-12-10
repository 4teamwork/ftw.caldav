from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.Permissions import webdav_access
from Products.CMFCore.utils import getToolByName
from ftw.caldav.browser.helpers import authenticated
from ftw.caldav.browser.proppatch import PROPPATCH
from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import ICalendar
from ftw.caldav.interfaces import IDAVReport
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from ftw.caldav.properties.calendars import CalendarsCollectionProperties
from ftw.caldav.utils import event_interface_identifiers
from lxml import etree
from plone.app.event.ical.importer import ical_import
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
import icalendar


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
        RESPONSE.setHeader('Allow', ', '.join(['PROPFIND', 'OPTIONS', 'PROPPATCH']))
        RESPONSE.setHeader('Content-Length', 0)
        RESPONSE.setHeader('DAV', '1, 2, calendar-access')
        RESPONSE.setStatus(200)
        return RESPONSE

    security.declareProtected(webdav_access, 'PROPPATCH')
    @authenticated
    def PROPPATCH(self, REQUEST, RESPONSE):
        """Retrieve OPTIONS.
        """
        member = self.getMember()
        provider = CalendarsCollectionProperties(member, self.request)
        return PROPPATCH(member, REQUEST, RESPONSE, provider=provider)


class CalendarView(BrowserView):
    implements(IPublishTraverse)

    security = ClassSecurityInfo()
    security.setPermissionDefault(webdav_access, ('Authenticated', 'Manager'))

    def __init__(self, context, request):
        super(CalendarView, self).__init__(context, request)
        self.path = None

    def publishTraverse(self, request, name):
        if name in dir(self):
            return getattr(self, name)

        elif self.path is not None:
            raise NotFound(self, name)

        else:
            self.path = name
            return self

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
        RESPONSE.setHeader('Allow', ', '.join(['PROPFIND', 'OPTIONS', 'REPORT',
                                               'PROPPATCH', 'PUT']))
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

    security.declareProtected(webdav_access, 'PROPPATCH')
    @authenticated
    def PROPPATCH(self, REQUEST, RESPONSE):
        """Retrieve OPTIONS.
        """
        return PROPPATCH(self.context, REQUEST, RESPONSE)

    security.declareProtected(webdav_access, 'PUT')
    @authenticated
    def PUT(self, REQUEST, RESPONSE):
        """PUT objects.
        """

        content_type = REQUEST.getHeader('Content-Type')
        if content_type != 'text/calendar':
            raise Exception('Unkown PUT content type: %s' % content_type)

        ical_data = REQUEST.get('BODY')
        ical_import(self.context, ical_data, 'plone.app.event.dx.event')

        cal = icalendar.Calendar.from_ical(ical_data)
        sync_uid = cal.walk('VEVENT')[0].decoded('UID')
        catalog = getToolByName(self.context, 'portal_catalog')
        brain = catalog(sync_uid=sync_uid,
                        path={'query': '/'.join(self.context.getPhysicalPath()),
                              'depth': 1})[0]
        RESPONSE.setHeader('ETag', '"%s"' % brain.UID)

        RESPONSE.setStatus(201)
        return RESPONSE
