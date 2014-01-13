# -*- coding: utf-8 -*-
from plone.app.layout import viewlets
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.i18nmessageid import MessageFactory
from collective.venusianconfig import configure
from collective.venusianconfig import scan

from venusianconfigdemo import views
from venusianconfigdemo import adapters
from venusianconfigdemo.interfaces import IVenusianConfigDemoLayer
from venusianconfigdemo.viewlets import LogoViewlet

_ = MessageFactory('venusianconfigdemo')

configure.i18n.registerTranslations(directory='locales')

configure.browser.resourceDirectory(
    name='venusianconfigdemo',
    directory='static'
)

scan(views)
scan(adapters)

configure.meta.provides(feature='demofeature')

configure.browser.page(
    name='hello-world-template',
    for_='*',
    template='templates/hello_world.pt',
    permission='zope2.View',
    condition='have demofeature'
)

configure.include(
    package='.portlets',
    file_='configure.py'
)

with configure(package=viewlets) as subconfigure:
    subconfigure.browser.viewlet(
        name='plone.logo',
        manager=IPortalHeader,
        klass=LogoViewlet,
        template='logo.pt',
        layer=IVenusianConfigDemoLayer,
        permission='zope2.View'
    )

configure.gs.registerProfile(
    name='default',
    title=_(u'Demonstration of venusian-configuration'),
    description=_(u'Install venusian-configured portlets'),
    directory='profiles/default',
    provides='Products.GenericSetup.interfaces.EXTENSION'
)

configure.include(package='collective.venusianconfig', file='meta.py')
