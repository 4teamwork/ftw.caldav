
def authenticated(method):
    """Protect a traversable method to require the visitor to be authenticated.
    This sets the method's __roles__. Without setting it the method is not
    traversable.
    """
    method.__roles__ = ('Authenticated', )
    return method
