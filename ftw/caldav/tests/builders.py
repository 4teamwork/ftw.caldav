from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class CalendarBuilder(DexterityBuilder):
    portal_type = 'ftw.caldav.Calendar'


builder_registry.register('calendar', CalendarBuilder)


class Event(DexterityBuilder):
    portal_type = 'plone.app.event.dx.event'

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        # ftw.builders auto-discovery does not work for recurrence:
        self.having(recurrence='')
        # using greenwich timezone
        self.having(timezone='Etc/Greenwich')

    def starting(self, date):
        return self.having(start=date)

    def ending(self, date):
        return self.having(end=date)

    def get_default_value_for_field(self, field):
        # "creators" default is not valid .....
        value = super(Event, self).get_default_value_for_field(field)
        if field.__name__ == 'creators' and value:
            return tuple([name.decode('utf-8') for name in value])
        return value

builder_registry.register('event', Event)
