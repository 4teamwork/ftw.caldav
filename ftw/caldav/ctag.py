from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from ftw.caldav.interfaces import ICalendar
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations


ANNOTATIONS_KEY = 'ftw.caldav:getctag'


def get_ctag(context):
    """Returns the currently stored ctag for the passed context.
    """
    annotations = IAnnotations(context)
    if ANNOTATIONS_KEY not in annotations:
        update_ctag(context)
    return annotations[ANNOTATIONS_KEY]


def update_ctag(context):
    """Update the ctag with a new one for the passed context.
    """
    annotations = IAnnotations(context)
    annotations[ANNOTATIONS_KEY] = compute_current_ctag(context)


def compute_current_ctag(context):
    """Returns a new ctag for the passed context.
    """
    uuid = IUUID(context)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f%z')
    return '-'.join((uuid, timestamp))


def update_calendar_ctag_handler(context, event):
    while not ICalendar.providedBy(context):
        context = aq_parent(aq_inner(context))
        if context is None:
            return

    update_ctag(context)
