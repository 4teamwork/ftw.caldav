from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


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
