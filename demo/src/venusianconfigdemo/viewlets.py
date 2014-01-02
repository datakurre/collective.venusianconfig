# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import ViewletBase


class LogoViewlet(ViewletBase):
    logo_tag = '<span>Logo</span>'
    navigation_root_title = u'Title'
