from ftw.caldav.interfaces import IDAVReport
from lxml import etree
from zope.interface import implements


class Report(object):
    implements(IDAVReport)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        raise NotImplementedError()

    def get_request_document(self):
        body = self.request.get('body')
        assert body and len(body) > 0, [body]
        return etree.fromstring(body)
