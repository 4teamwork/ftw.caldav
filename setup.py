import os
from setuptools import setup, find_packages


version = '1.2.1.dev0'


extras_require = {
    'calendar': ['plone.app.dexterity'],
    'events': ['plone.app.event>=1.0.3'],
    }

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'plone.app.dexterity',
    'plone.app.event',
    'plone.app.testing',
    'unittest2',
    'zope.configuration',
    ] + reduce(list.__add__, extras_require.values())

extras_require['tests'] = tests_require


setup(name='ftw.caldav',
      version=version,
      description='CalDAV support for Plone.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw caldav plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.caldav',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'collective.monkeypatcher',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
