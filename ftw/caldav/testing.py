from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class CaldavLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import ftw.caldav
        xmlconfig.file('configure.zcml',
                       ftw.caldav,
                       context=configurationContext)


CALDAV_FIXTURE = CaldavLayer()

CALDAV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CALDAV_FIXTURE, ),
    name='ftw.caldav:integration')

CALDAV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CALDAV_FIXTURE, ),
    name="ftw.caldav:functional")

CALDAV_ZSERVER_FUNCTIONAL_TESTING  = FunctionalTesting(
    bases=(CALDAV_FIXTURE, PLONE_ZSERVER),
    name="ftw.caldav:functional:zserver")
