from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from ftw.caldav.properties.adapter import CalDAVPropertiesAdapter
from ftw.caldav.properties.adapter import caldav_callback
from ftw.caldav.properties.adapter import caldav_property
from ftw.caldav.utils import portal_url_prefix
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

    @caldav_property('calendar-home-set', 'urn:ietf:params:xml:ns:caldav')
    @caldav_callback
    def calendar_home_set(self, parent_node):
        """http://tools.ietf.org/html/rfc4791#section-6.2.1
        Identifies the URL of any WebDAV collections that contain
        calendar collections owned by the associated principal resource.
        """
        etree.SubElement(parent_node, '{DAV:}href').text = '/'.join(
            (portal_url_prefix(), 'caldav-calendars', self.context.getId()))

    @caldav_property('current-user-principal', 'DAV:')
    @caldav_callback
    def current_user_principal(self, parent_node):
        """http://tools.ietf.org/html/rfc5397#section-3
        Indicates a URL for the currently authenticated user's
        principal resource on the server.
        """

        portal_url = getToolByName(self.context, 'portal_url')
        etree.SubElement(parent_node, '{DAV:}href').text = '/'.join(
            (portal_url(), 'caldav-principal', self.context.getId()))

    @caldav_property('calendar-user-address-set', 'urn:ietf:params:xml:ns:caldav')
    @caldav_callback
    def calendar_user_address_set(self, parent_node):
        """http://tools.ietf.org/html/rfc6638#section-2.4.1
        Identify the calendar addresses of the associated principal
        resource.
        """

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if member.getProperty('email'):
            etree.SubElement(parent_node, '{DAV:}href').text = 'mailto:%s' % (
                member.getProperty('email'))

        etree.SubElement(parent_node, '{DAV:}href').text = 'userid:%s' % (
            member.getId())

        etree.SubElement(parent_node, '{DAV:}href').text = '/'.join(
            (portal_url_prefix(), 'caldav-principal', member.getId()))

        portal_url = getToolByName(self.context, 'portal_url')
        etree.SubElement(parent_node, '{DAV:}href').text = '/'.join(
            (portal_url(), 'caldav-principal', member.getId()))
