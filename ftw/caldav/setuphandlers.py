from ftw.caldav.propertysheets import CalDAVProperties


def install_caldav(context):
    """Installs ftw.caldav.
    """

    if context.readDataFile('ftw.caldav.txt') is None:
        return

    platform = context.getSite()
    install_caldav_property_sheet(platform)


def install_caldav_property_sheet(platform):
    """Installs an additional property sheet on the Plone site root for
    caldav properties.
    """
    platform.propertysheets.addPropertySheet(CalDAVProperties())
