# -*- coding: utf-8 -*-
from collective.venusianconfig import configure
from collective.venusianconfig import scan

from venusianconfigdemo import views
from venusianconfigdemo import adapters

configure.browser.resourceDirectory(
    name='venusianconfigdemo',
    directory='static'
)

scan(views)
scan(adapters)

configure.browser.page(
    name='hello-world-template',
    for_='*',
    template='templates/hello_world.pt',
    permission='zope2.View',
)

configure.include(
    package='.portlets',
    file_='configure.py'
)

configure.gs.registerProfile(
    name='default',
    title=u'Demonstration of venusian-configuration',
    description=u'Install venusian-configured portlets',
    directory='profiles/default',
    provides='Products.GenericSetup.interfaces.EXTENSION'
)
