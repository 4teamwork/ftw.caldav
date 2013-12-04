from zope.interface import Interface


class ICalDAVProperties(Interface):
    """An adapter providing caldav properties.
    """

    def __init__(context, request):
        """Adapts context and request.
        """

    def get_properties(names=None):
        """Get all properties or a certain set of properties identifed by names.
        """
