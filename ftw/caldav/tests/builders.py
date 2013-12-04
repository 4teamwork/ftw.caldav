from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class CalendarBuilder(DexterityBuilder):
    portal_type = 'ftw.caldav.Calendar'


builder_registry.register('calendar', CalendarBuilder)
