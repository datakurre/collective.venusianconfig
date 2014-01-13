# -*- coding: utf-8 -*-
import inspect
from uuid import uuid4

import zope.configuration
from Products.Five import BrowserView
from Products.Five.browser.metaconfigure import page
from zope.browserpage.metadirectives import IPagesDirective
from zope.browserpage.metadirectives import IPagesPageSubdirective
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from venusianconfiguration import directive_config


class IViewDirective(IPagesDirective, IPagesPageSubdirective):
    """The page directive is used to create views that provide a single
    url or page.

    The page directive creates a new view class from a given template
    and/or class and registers it.

    """
    handler = zope.configuration.fields.GlobalObject(
        title=u"Handler",
        description=u"A callable object that handles view logic.",
        required=False,
    )


class BrowserViewCallable(BrowserView):
    def __call__(self):
        results = self._callable(self.context, self.request)
        if type(results) == dict:
            self.__dict__.update(results)
            return self.index()
        else:
            return results


@directive_config(name="page_config",
                  namespace="http://namespaces.plone.org/plone",
                  schema=IViewDirective)
def page_config(_context, name, permission, for_,
                layer=IDefaultBrowserLayer, template=None, class_=None,
                allowed_interface=None, allowed_attributes=None,
                attribute='__call__', menu=None, title=None, handler=None):

    if inspect.isfunction(handler):
        class_ = type('{0:s}{1:s}'.format(str(uuid4()).replace('-', ''),
                                          str(name)),
                      (BrowserViewCallable,),
                      {"_callable": staticmethod(handler)})
    elif inspect.isclass(handler):
        class_ = handler

    page(_context, name, permission, for_, layer=layer, template=template,
         class_=class_, allowed_interface=allowed_interface,
         allowed_attributes=allowed_attributes, attribute=attribute,
         menu=menu, title=title)
