venusianconfiguration
=====================

This package (*venusianconfiguration*) provides venusian_ based Python
configuration syntax for `zope.configuration`_ as an alternative to zcml.
This package does not replace *zope.configuration* like *grok* used to
do, but just provides generic Python bindings for existing
*zope.configuration* directives.

The current status of this package is "already in internal use, but maybe
not yet ready for he community".

The good:

.. code:: python

   from venusianconfiguration import configure

   @configure.browser.page(
       name='hello-world', for_=Interface,
       permission='zope2.View')
   class HelloWorld(BrowserView):
       def __call__(self):
           return u'Hello world!'

The bad:

.. code:: python

   from venusianconfiguration import scan
   from venusianconfiguration import configure

   from mypackage import browser
   scan(browser)

   import otherpackage
   configure.include(otherpackage, file='configure.py')

The ugly:

*zope.configuration* is mostly syntax-agnostic, but unfortunately
we have
been using its ZCML-specific API-directly.




.. _venusian: https://pypi.python.org/pypi/venusian
.. _zope.configuration: https://pypi.python.org/pypi/zope.configuration

.. image:: https://travis-ci.org/datakurre/collective.venusianconfig.png
   :target: http://travis-ci.org/datakurre/collective.venusianconfig

Usage
-----

.. code:: ini

   [instance]
   recipe = plone.recipe.zope2instance
   ...
   eggs =
       ...
       venusianconfiguration
   zope-conf-additional =
       %import venusianconfiguration
   site-zcml =
       <configure
           xmlns="http://namespaces.zope.org/zope"
           xmlns:meta="http://namespaces.zope.org/meta"
           xmlns:five="http://namespaces.zope.org/five">

       <include package="Products.Five" />
       <meta:redefinePermission from="zope2.Public" to="zope.Public" />

       <!-- Load the meta -->
       <include files="package-includes/*-meta.zcml" />
       <five:loadProducts file="meta.zcml"/>
       <includePlugins package="plone" file="meta.py" />

       <!-- Load the configuration -->
       <include files="package-includes/*-configure.zcml" />
       <five:loadProducts />
       <includePlugins package="plone" file="configure.py" />

       <!-- Load the configuration overrides-->
       <includeOverrides files="package-includes/*-overrides.zcml" />
       <five:loadProductsOverrides />
       <includePluginsOverrides package="plone" file="overrides.py" />

       <securityPolicy
           component="AccessControl.security.SecurityPolicy" />

       </configure>
