
def _traversable(method):
    # Decorator for making webdav methods traversable by setting the __roles__
    # to the default empty string.
    # Otherwise the Zope traversal would not allow to call it.
    method.__roles__ = ''
    return method
