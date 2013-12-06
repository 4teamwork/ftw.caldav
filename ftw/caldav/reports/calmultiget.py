from ftw.caldav.interfaces import ICalDAVProperties
from ftw.caldav.interfaces import IPROPFINDDocumentGenerator
from ftw.caldav.interfaces import NAMESPACES
from ftw.caldav.interfaces import PROP_PROPNAMES
from ftw.caldav.reports import Report
from ftw.caldav.utils import parse_property_request
from lxml import etree
from urlparse import urlparse
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite


class CalendarMultigetReport(Report):

    def __call__(self):
        request_body = self.request.get('BODY')
        prop_mode, properties = parse_property_request(request_body)
        names_only = prop_mode == PROP_PROPNAMES

        document = etree.Element('{DAV:}multistatus', nsmap=NAMESPACES)
        generator = getAdapter(self.request, IPROPFINDDocumentGenerator)

        for obj in self.get_requested_objects():
            provider = getMultiAdapter((obj, self.request), ICalDAVProperties)
            generator.add_response(document,
                                   provider,
                                   select_properties=properties,
                                   names_only=names_only)

        return etree.tostring(document, pretty_print=True)

    def get_requested_objects(self):
        root = etree.fromstring(self.request.get('BODY'))
        site = getSite()

        objects = []
        for href in root.xpath('//dav:href', namespaces=NAMESPACES):
            path = urlparse(href.text.strip()).path.rstrip('caldav')
            obj = site.restrictedTraverse(path)
            objects.append(obj)

        return objects
