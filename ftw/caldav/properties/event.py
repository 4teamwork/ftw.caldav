from Products.CMFCore.utils import getToolByName
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from lxml import etree
from plone.event.interfaces import IEvent
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.interface import Interface


class EventProperties(CalDAVPropertiesAdapter):
    """Property representation for p.a.event events.
    """
    adapts(IEvent, Interface)

    def get_href(self):
        return '/'.join((self.context.absolute_url(), 'caldav'))

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

    @caldav_property('getetag', 'DAV:')
    def getetag(self):
        """http://tools.ietf.org/html/rfc2518#section-13.6
        """
        return '"%s"' % IUUID(self.context)
