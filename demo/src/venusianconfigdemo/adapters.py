# -*- coding: utf-8 -*-

from collective.venusianconfig import configure

import logging


@configure.subscriber.handler(
    for_=('Products.CMFCore.interfaces.IContentish',
          'zope.lifecycleevent.IObjectModifiedEvent'))
def logObjectModifiedEvent(context, event):
    logging.info('{0:s} modified'.format(context))
