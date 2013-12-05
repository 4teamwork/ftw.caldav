from Products.CMFCore.utils import getToolByName
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
