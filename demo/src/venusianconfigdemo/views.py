# -*- coding: utf-8 -*-

from venusianconfiguration import configure
from venusianconfiguration import page_config

from Products.Five.browser import BrowserView


@configure.browser.page.klass(name='hello-world', context='*',
                              permission='zope2.View')
class HelloWorld(BrowserView):

    def __call__(self):
        return u"Hello world"


@page_config(name='hello-world-2', for_='*', permission='zope2.View')
class HelloWorld2(BrowserView):

    def __call__(self):
        return u"Hello world"


@page_config(name='hello-world-handler', for_='*', permission='zope2.View')
def hello_world_handler(context, request):
    return u"Hello World!"


@page_config(name='hello-world-handler-template',
             for_='*', permission='zope2.View',
             template='templates/hello_world.pt')
def hello_world_template_handler(context, request):
    return {'content': u'Hello New World!'}
