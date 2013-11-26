# -*- coding: utf-8 -*-
import logging

from Products.CMFCore.interfaces import IContentish
from zope.lifecycleevent import IObjectModifiedEvent

from collective.venusianconfig import configure


@configure.subscriber.handler(for_=(IContentish, IObjectModifiedEvent))
def logObjectModifiedEvent(context, event):
    logging.info('{0:s} modified'.format(context))
