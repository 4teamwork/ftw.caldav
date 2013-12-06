from AccessControl import getSecurityManager
from BTrees.OOBTree import OOBTree
from ftw.caldav.interfaces import ICalDAVProperties
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces import NotFound


ANNOTATIONS_CONTEXT_KEY = 'ftw.caldav: context properties'
ANNOTATIONS_USER_KEY = 'ftw.caldav: user properties'


def caldav_property(name, namespace):
    def wrapper(func):
        if getattr(func, '_caldav_property', None) is None:
            func._caldav_property = {}

        func._caldav_property.update({
                'name': name,
                'namespace': namespace})
        return func
    return wrapper


def caldav_callback(func):
    if getattr(func, '_caldav_property', None) is None:
        func._caldav_property = {}

    func._caldav_property['callback'] = True
    return func


class CalDAVPropertiesAdapter(object):
    implements(ICalDAVProperties)
    adapts(Interface, Interface)

    properties = ()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_href(self):
        raise NotImplementedError()

    def get_subelements(self):
        return []

    def get_properties(self, names=None, names_only=False):
        result = []

        for property_info in self._discover_properties():
            if names is not None and property_info['name'] not in names:
                continue

            if names_only:
                result.append({'name': property_info['name'],
                               'namespace': property_info['namespace'],
                               'status_code': 200})
                continue

            if property_info['is_callback']:
                result.append({'name': property_info['name'],
                               'namespace': property_info['namespace'],
                               'status_code': 200,
                               'callback': property_info['method']})

            else:
                status_code = 200
                try:
                    value = property_info['method']()
                except NotFound:
                    status_code = 404
                    value = None
                result.append({'name': property_info['name'],
                               'namespace': property_info['namespace'],
                               'status_code': status_code,
                               'value': value})

        return result

    def _discover_properties(self):
        properties = []

        for name in dir(self):
            method = getattr(self, name, None)
            if not hasattr(method, '_caldav_property'):
                continue

            property_settings = method._caldav_property
            properties.append(
                {'name': property_settings['name'],
                 'namespace': property_settings['namespace'],
                 'method': method,
                 'is_callback': property_settings.get('callback', False)})

        def property_getter(property):
            def getter():
                return self.get_property_from_storage(property['storage'],
                                                      property['namespace'],
                                                      property['name'])
            return getter

        for property in self.properties:
            properties.append(
                {'name': property['name'],
                 'namespace': property['namespace'],
                 'is_callback': False,
                 'method': property_getter(property)})

        properties.sort(key=lambda info: info.get('name'))
        return properties

    def get_property_from_storage(self, storage_name, namespace, name):
        storage = self.get_storage(storage_name)
        key = (namespace, name)
        if key not in storage:
            raise NotFound(self, str(key))
        return storage[key]

    def set_property_in_storage(self, storage_name, namespace, name, value):
        storage = self.get_storage(storage_name)
        key = (namespace, name)
        storage[key] = value

    def set_property(self, namespace, name, value):
        found = False
        for property in self.properties:
            if property['namespace'] == namespace and property['name'] == name:
                found = True
                break

        if not found:
            raise NotFound(self.context, (namespace, name))

        return self.set_property_in_storage(property['storage'], namespace,
                                            name, value)

    def get_storage(self, storage_name):
        annotations = IAnnotations(self.context)
        if storage_name == 'context':
            if ANNOTATIONS_USER_KEY not in annotations:
                annotations[ANNOTATIONS_CONTEXT_KEY] = OOBTree()

            return annotations[ANNOTATIONS_CONTEXT_KEY]

        elif storage_name == 'user':
            if ANNOTATIONS_USER_KEY not in annotations:
                annotations[ANNOTATIONS_USER_KEY] = OOBTree()

            users = annotations[ANNOTATIONS_USER_KEY]
            user_id = getSecurityManager().getUser().getId()
            if user_id not in users:
                users[user_id] = OOBTree()
            return users

        else:
            raise ValueError('Unkown storage: "%s"' % storage_name)
