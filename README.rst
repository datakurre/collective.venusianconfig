venusianconfiguration
=====================

This package (**venusianconfiguration**) provides venusian_ based Python
configuration syntax for `zope.configuration`_ as an alternative to zcml.
This package does not replace **zope.configuration** like **grok** used to do,
but just provides generic Python bindings for existing zope.configuration
directives.
So, venusianconfiguration is more an alternative to grok than it is to
zope.configuration.

The current status of this package can be described as *already in internal
use, but maybe not yet ready for the community*.

.. _venusian: https://pypi.python.org/pypi/venusian
.. _zope.configuration: https://pypi.python.org/pypi/zope.configuration

.. image:: https://travis-ci.org/datakurre/collective.venusianconfig.png
   :target: http://travis-ci.org/datakurre/collective.venusianconfig

The good:

.. code:: python

   from venusianconfiguration import configure

   configure.i18n.registerTranslations(directory='locales')

   @configure.browser.page.klass(
       name='hello-world', for_=Interface,
       permission='zope2.View')
   class HelloWorld(BrowserView):
       def __call__(self):
           return u'Hello world!'

   @configure.plone.behavior.provides(
       title=_(u'My behavior),
       description=_(u'Enables magic'))
   class IMyBehavior(model.Schema):
       custom_field = schema.TextLine()
   alsoProvides(IMyBehavior, IFormFieldProvider)

The bad:

.. code:: python

   from venusianconfiguration import scan
   from venusianconfiguration import configure

   from mypackage import browser
   scan(browser)

   import zcmlpackage
   configure.include(package=zcmlpackage)

   import otherpypackage
   configure.include(package=otherpypackage, file='configure.py')

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

To support **z3c.autoinclude**, **venusianconfiguration** also monkeypatches
z3c.autoincludes's includePluginsDirective and includePluginsOveridesDirective
(includeDependencies-directive is considered evil and is intentionally left
unsupported).

So, three monkeypatches in total for zcml-free configuration.


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
       # Enable venuasianconfiguration monkeypatches
       %import venusianconfiguration

For more examples, look into the demo-package included in the sources.
