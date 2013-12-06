from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from ftw.caldav.ctag import get_ctag
from ftw.caldav.interfaces import ICalendar
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from lxml import etree
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.interface import Interface
import icalendar


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

    properties = (
        {'name': 'calendar-color',
         'namespace': 'http://apple.com/ns/ical/',
         'storage': 'user'},

        {'name': 'calendar-order',
         'namespace': 'http://apple.com/ns/ical/',
         'storage': 'user'}, )

    def get_href(self):
        return '/'.join((self.context.absolute_url(), 'caldav'))

    @caldav_property('resourcetype', 'DAV:')
    @caldav_callback
    def resourcetype(self, parent_node):
        """http://tools.ietf.org/html/rfc4791#section-4.2
        """
        etree.SubElement(parent_node, '{DAV:}collection')
        etree.SubElement(parent_node, '{urn:ietf:params:xml:ns:caldav}calendar')

    @caldav_property('displayname', 'DAV:')
    def displayname(self):
        """http://tools.ietf.org/html/rfc2518#section-13.2
        """
        return self.context.Title()

    @caldav_property('resource-id', 'DAV:')
    def resource_id(self):
        """http://tools.ietf.org/html/rfc5842#section-3.1
        """
        return 'uuid:%s' % IUUID(self.context)

    @caldav_property('owner', 'DAV:')
    @caldav_callback
    def owner(self, parent_node):
        """http://tools.ietf.org/html/rfc3744#section-5.1
        """

        portal_url = getToolByName(self.context, 'portal_url')
        owner_id = self.context.getOwner().getId()
        etree.SubElement(parent_node, '{DAV:}href').text = '/'.join(
            (portal_url(), 'caldav-principal', owner_id))

    @caldav_property('getcontenttype', 'DAV:')
    def getcontenttype(self):
        """http://tools.ietf.org/html/rfc2518#section-13.5
        """
        return 'text/calendar; component=vevent'


    @caldav_property('calendar-description', 'urn:ietf:params:xml:ns:caldav')
    def calendar_description(self):
        """http://tools.ietf.org/html/rfc4791#section-5.2.1
        """
        return self.context.Description()

    @caldav_property('supported-calendar-component-set',
                     'urn:ietf:params:xml:ns:caldav')
    @caldav_callback
    def supperted_calendar_component_set(self, parent_node):
        """http://tools.ietf.org/html/rfc4791#section-5.2.3
        """
        etree.SubElement(parent_node, '{urn:ietf:params:xml:ns:caldav}comp',
                         {'name': 'VEVENT'})

    @caldav_property('calendar-timezone', 'urn:ietf:params:xml:ns:caldav')
    def calendar_timezone(self):
        """http://tools.ietf.org/html/rfc4791#section-5.2.2
        """
        try:
            from plone.app.event.base import default_timezone
        except ImportError:
            timezone = 'UTC'
        else:
            timezone = default_timezone()

        calendar = icalendar.Calendar()
        tzc = icalendar.Timezone()
        tzc.add('tzid', timezone)
        calendar.add_component(tzc)
        return calendar.to_ical()

    @caldav_property('getctag', 'http://calendarserver.org/ns/')
    def getctag(self):
        """http://tinyurl.com/oz8t32w
        """
        return get_ctag(self.context)
