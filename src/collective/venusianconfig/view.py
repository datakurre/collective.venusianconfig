# -*- coding: utf-8 -*-

from collective.venusianconfig import configure

from Products.Five.browser import BrowserView


@configure.browser.view.klass(name='hello-world', context='*',
                              permission='zope2.View')
class HelloWorld(BrowserView):

    def __call__(self):
        return u"Hello world"
