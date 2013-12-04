from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from ftw.caldav.interfaces import ICalendar
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from lxml import etree
from zope.component import adapts
from zope.interface import Interface


class CalendarsCollectionProperties(CalDAVPropertiesAdapter):
    """Represents the calendars list of a user.
    This "adapter" is not registered and is instantiated directly by the calendars
    listing view.
    """
    adapts(IMemberData, Interface)

    def get_href(self):
        urltool = getToolByName(self.context, 'portal_url')
        return '/'.join((urltool(), 'caldav-calendars', self.context.getId()))

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        """http://tools.ietf.org/html/rfc4791#section-4.2
        """
        etree.SubElement(parent_node, '{DAV:}collection')


class CalendarProperties(CalDAVPropertiesAdapter):
    adapts(ICalendar, Interface)

    def get_href(self):
        return '/'.join((self.context.absolute_url(), 'caldav'))

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        """http://tools.ietf.org/html/rfc4791#section-4.2
        """
        etree.SubElement(parent_node, '{urn:ietf:params:xml:ns:caldav}calendar')

    @caldav_property('displayname', 'DAV:')
    def displayname(self):
        return self.context.Title()
