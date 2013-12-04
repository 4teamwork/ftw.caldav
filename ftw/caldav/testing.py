from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.dexterity.fti import DexterityFTI
from zope.configuration import xmlconfig
import  ftw.caldav.tests.builders


class CaldavLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        import ftw.caldav
        xmlconfig.file('configure.zcml',
                       ftw.caldav,
                       context=configurationContext)

        import plone.app.dexterity
        xmlconfig.file('configure.zcml',
                       plone.app.dexterity,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.caldav:default')
        applyProfile(portal, 'ftw.caldav:calendar')


CALDAV_FIXTURE = CaldavLayer()

CALDAV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CALDAV_FIXTURE, ),
    name='ftw.caldav:integration')

CALDAV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CALDAV_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.caldav:functional")

CALDAV_ZSERVER_FUNCTIONAL_TESTING  = FunctionalTesting(
    bases=(CALDAV_FIXTURE,
           PLONE_ZSERVER,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.caldav:functional:zserver")
