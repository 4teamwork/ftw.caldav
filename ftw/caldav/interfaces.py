from zope.interface import Interface


class ICalDAVProperties(Interface):
    """An adapter providing caldav properties.
    """

    def __init__(context, request):
        """Adapts context and request.
        """

    def get_href():
        """Returns the URL of the CalDAV representation of the current object.
        This may include a view name or not.
        """

    def get_properties(names=None):
        """Get all properties or a certain set of properties identifed by names.
        """

    def get_subelements():
        """Returns all sub element relevant for the CalDAV implementation.
        """


class IPROPFINDDocumentGenerator(Interface):
    """Adapter for generating a PROPFIND XML response document.
    The adapter supports to create a new document or extend an existing document
    from another document generator.
    """

    def __init__(request):
        """Adapts the request.
        """

    def create_document():
        """Creates a new "multistatus" document and returns the document root.
        The document root needs to be passed into following calls to this or other
        generators.
        """

    def add_response(document, properties_provider, select_properties=None,
                     names_only=False):
        """Add a response section to the passed `document` containing information
        provided by the ICalDAVProperties adapter `properties_provider`.

        With the optional argument `properties` the properties can be limited.
        It is expected to be a list of tuples, each containing the name of the property
        and the XML-namespace it is defined in.
        """

    def generate(property_providers):
        """Generate the XML response for the PROPFIND request by reading the request
        information and writing to the response directly at the end.

        For each property provider (``property_providers``), a response in the
        PROPFIND request is generated. Each provider must implement ICalDAVProperties.
        """
