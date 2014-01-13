# -*- coding: utf-8 -*-
from venusianconfiguration import i18n_domain
from venusianconfiguration import configure
from venusianconfigdemo.portlets import venusianportlet

i18n_domain('venusianconfigdemo')

configure.include(package='plone.app.portlets')

configure.plone.portlet(
    name='venusianconfigdemo.venusianportlet',
    interface=venusianportlet.IVenusianPortlet,
    renderer=venusianportlet.Renderer,
    assignment=venusianportlet.Assignment,
    addview=venusianportlet.AddForm,
    editview=venusianportlet.EditForm
)
