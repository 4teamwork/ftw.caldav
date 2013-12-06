from Products.CMFCore.utils import getToolByName
from ftw.caldav.interfaces import NAMESPACES
from ftw.caldav.interfaces import PROP_ALLPROPS
from ftw.caldav.interfaces import PROP_PROPNAMES
from ftw.caldav.interfaces import PROP_SELECTPROPS
from lxml import etree
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.dottedname.resolve import resolve


def portal_url_prefix():
    """Returns the URL path prefix to the Plone site root (portal)
    respecting the virtual host monster configuration.
    This is necessary because we usually do not return the full URL in webdav
    properties but only the path.
    """
    portal = getSite()
    portal_url = getToolByName(portal, 'portal_url')
    url = portal_url()

    # remove protocol
    _, url = url.split('://', 1)
    # remove host / port part
    _, url = url.split('/', 1)
    return '/' + url


def event_interfaces():
    """Returns the list of configured interfaces for event types.
    Not importable interfaces are filtered silently.
    """

    from plone.registry.interfaces import IRegistry
    registry = getUtility(IRegistry)
    interface_names = registry.get('ftw.caldav.event_interfaces', [])

    interfaces = []
    for dottedname in interface_names:
        try:
            interfaces.append(resolve(dottedname))
        except ImportError:
            pass

    return interfaces


def event_interface_identifiers():
    """Returns of identifiers (string) of all configured event type interfaces.
    Not existing / not importable interfaces are filtered silently.
    """
    return map(lambda iface: iface.__identifier__, event_interfaces())


def parse_property_request(request_data):
    """Parses a WebDAV property request (PROPFIND, REPORT, ...) and returns the
    requested mode and the list of properties as tuple of tagname and namespace.

    Supported modes:

    <DAV:propname> -- The names of supported properties should be returned,
    without values.
    Example: (PROP_PROPNAMES, None)

    <DAV:allprop> -- Return all property values.
    Example: (PROP_ALLPROPS, None)

    <DAV:prop> -- Return selected property values only.
    Example: (PROP_SELECTPROPS, [('displayname', 'DAV:')])
    """

    root = etree.fromstring(request_data)

    if root.xpath('//dav:propname', namespaces=NAMESPACES):
        return PROP_PROPNAMES, None

    elif root.xpath('//dav:allprop', namespaces=NAMESPACES):
        return PROP_ALLPROPS, None

    properties = []
    for property in root.xpath('//dav:prop/*', namespaces=NAMESPACES):
        # property.tag is -> '{namespace}tagname'
        namespace, tagname = property.tag.lstrip('{').split('}')
        properties.append((tagname, namespace))
    return PROP_SELECTPROPS, properties


def parse_proppatch_request(request_data):
    """Parses the WebDAV PROPPATCH request body and returns a list of properties to
    patch, each consisting of a tuple with namespace, name and new value.
    """

    root = etree.fromstring(request_data)
    if root.xpath('//dav:remove', namespaces=NAMESPACES):
        raise Exception('dav:remove not yet implemented')

    properties = []
    for node in root.xpath('//dav:set/dav:prop/*', namespaces=NAMESPACES):
        # property.tag is -> '{namespace}tagname'
        namespace, tagname = node.tag.lstrip('{').split('}')
        value = node.text
        properties.append((namespace, tagname, value))

    return properties
