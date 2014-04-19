venusianconfiguration
=====================

This package (**venusianconfiguration**) provides venusian_ based Python
configuration syntax for `zope.configuration`_ as an alternative to zcml.
This package does not replace **zope.configuration** like **grok** used to
do, but just provides generic Python bindings for existing
zope.configuration directives. So, venusianconfiguration is more an
alternative to grok than it is to zope.configuration.

The current status of this package can be described as *already in internal
use, but maybe not yet ready for he community*.

.. _venusian: https://pypi.python.org/pypi/venusian
.. _zope.configuration: https://pypi.python.org/pypi/zope.configuration

.. image:: https://travis-ci.org/datakurre/collective.venusianconfig.png
   :target: http://travis-ci.org/datakurre/collective.venusianconfig

The good:

.. code:: python

   from venusianconfiguration import configure

   configure.i18n.registerTranslations(directory='locales')

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

   import zcmlpackage
   configure.include(package=otherpackage)

   import otherpackage
   configure.include(package=otherpackage, file='configure.py')

   import mypackage.submodule
   configure.include(package=mypackage.submodule,
                     file='configure.py')

The ugly:

**zope.configuration** is mostly syntax-agnostic, but unfortunately
ZCML has been the only implemented syntax for it and we have also
used to call its ZCML-specific API directly (e.g. in test fixtures
and in z3c.autoinclude).

Therefore a new zope.configuration syntax cannot be introduced outside
zope.configuration without monkeypatching...

**venusianconfiguration** works by monkeypatching the processxmlfile
method in **zope.configuration**'s ZCML-support to accept also Python
files pass those to venusianconfiguration to process.

Also, in addition to that monkeypatch, a custom `site.zcml`-file is
required to make z3c.autoinclude load also venusianconfigured packges.

Todo:

- Add monkeypatch for z3c.autoinclude to try also .py-files when
  .zcml-files do not exist to get rid of the need for custom
  site.zcml

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

For examples, look into the demo-package included in the sources.
