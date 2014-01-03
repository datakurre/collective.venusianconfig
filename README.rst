This is just an experiment of using zope.configuration with venusian instead
of zcml-files.

Usage
-----

.. code:: ini

   [instance]
   recipe = plone.recipe.zope2instance
   ...
   eggs =
       ...
       collective.venusianconfig
   zope-conf-additional =
       %import collective.venusianconfig
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
