from ftw.caldav.interfaces import ICalDAVProperties
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements


def caldav_property(name, namespace):
    def wrapper(func):
        setattr(func, '_caldav_property', {
                'name': name,
                'namespace': namespace})
        return func
    return wrapper


class CalDAVPropertiesAdapter(object):
    implements(ICalDAVProperties)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_properties(self, names=None):
        result = []

        for property_info in self._discover_properties():
            if names is not None and property_info['name'] not in names:
                continue

            result.append({'name': property_info['name'],
                           'namespace': property_info['namespace'],
                           'status_code': 200,
                           'value': property_info['method']()})

        return result

    def _discover_properties(self):
        properties = []

        for name in dir(self):
            method = getattr(self, name, None)
            if not hasattr(method, '_caldav_property'):
                continue

            property_settings = method._caldav_property
            properties.append({'name': property_settings['name'],
                               'namespace': property_settings['namespace'],
                               'method': method})

        properties.sort(key=lambda info: info.get('name'))
        return properties
