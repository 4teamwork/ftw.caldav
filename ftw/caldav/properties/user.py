from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from lxml import etree
from zope.component import adapts
from zope.interface import Interface


class UserCalDAVProperties(CalDAVPropertiesAdapter):
    adapts(IMemberData, Interface)

    def get_href(self):
        urltool = getToolByName(self.context, 'portal_url')
        return '/'.join((urltool(), 'caldav-principal', self.context.getId()))

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        """http://tools.ietf.org/html/rfc3744#section-4
        "PROPFIND" on the principal view must return a DAV:resourcetype
        of "DAV:principal".
        """
        etree.SubElement(parent_node, '{DAV:}principal')

    @caldav_property('displayname', 'DAV:')
    def displayname(self):
        """http://tools.ietf.org/html/rfc3744#section-4
        The principal should have a non-empty "displayname" property."""
        return self.context.getProperty('fullname') or self.context.getId()

    @caldav_property('calendar-home-set', 'DAV:')
    def calendar_home_set(self):
        """http://tools.ietf.org/html/rfc4791#section-6.2.1
        Identifies the URL of any WebDAV collections that contain
        calendar collections owned by the associated principal resource.
        """
        urltool = getToolByName(self.context, 'portal_url')
        return '/'.join((urltool(), 'caldav-calendars', self.context.getId()))
