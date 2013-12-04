from ftw.caldav.interfaces import ICalendar
from plone.dexterity.content import Container
from zope.interface import Interface
from zope.interface import implements


class ICalendarSchema(Interface):
    pass


class Calendar(Container):
    implements(ICalendar)
