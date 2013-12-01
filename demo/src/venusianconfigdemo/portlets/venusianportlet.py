# -*- coding: utf-8 -*-
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from z3c.form import field
from plone.app.portlets.browser import z3cformhelper as form

_ = MessageFactory('venusianconfigdemo')


class IVenusianPortlet(IPortletDataProvider):
    """This portlet has no options"""


class Assignment(base.Assignment):
    implements(IVenusianPortlet)

    @property
    def title(self):
        return _('venusianportlet_title', default=u'Venusian Portlet')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('venusianportlet.pt')
    title = _('venusianportlet_title', default=u'Venusian Portlet')

    @property
    def available(self):
        return True

    def __call__(self, *args, **kwargs):
        import pdb; pdb.set_trace()
        super(Renderer, self).__call__(*args, **kwargs)


class AddForm(form.AddForm):

    fields = field.Fields(IVenusianPortlet)

    label = _(u'Add portlet')
    description = _('venusianportlet_description',
                    default=u'This is a venusian-configured portlet.')

    def create(self, data):
        return Assignment(**data)


class EditForm(form.EditForm):

    fields = field.Fields(IVenusianPortlet)

    label = _(u'Edit portlet')
    description = _('venusianportlet_description',
                    default=u'This is a venusian-configured portlet.')
