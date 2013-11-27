# -*- coding: utf-8 -*-
import imp
import os
import sys
from pkgutil import ImpLoader

import venusian
from zope.configuration.xmlconfig import ParserInfo


NAMESPACES = {
    'apidoc': 'http://namespaces.zope.org/apidoc',
    'browser': 'http://namespaces.zope.org/browser',
    'cache': 'http://namespaces.zope.org/cache',
    'cmf': 'http://namespaces.zope.org/cmf',
    'five': 'http://namespaces.zope.org/five',
    'genericsetup': 'http://namespaces.zope.org/genericsetup',
    'grok': 'http://namespaces.zope.org/grok',
    'gs': 'http://namespaces.zope.org/genericsetup',
    'i18n': 'http://namespaces.zope.org/i18n',
    'kss': 'http://namespaces.zope.org/kss',
    'meta': 'http://namespaces.zope.org/meta',
    'monkey': 'http://namespaces.zope.org/monkey',
    'plone': 'http://namespaces.plone.org/plone',
    'z3c': 'http://namespaces.zope.org/z3c',
    'zcml': 'http://namespaces.zope.org/zcml',
    'zope': 'http://namespaces.zope.org/zope',
}

ARGUMENT_MAP = {
    'file_': 'file',
    'for_': 'for',
    'adapts': 'for',
    'context': 'for',
    'klass': 'class',
    'class_': 'class',
}

CALLABLE_ARGUMENTS = [
    'class',
    'factory',
    'handler'
]


class ConfigureMetaProxy(object):

    def __init__(self, klass, value):
        self._klass = klass
        self._value = value

    def __getattr__(self, attr_name):
        return getattr(self._klass, '{0}|{1}'.format(self._value, attr_name))

    def __call__(self, *args, **kwargs):
        return self._klass(self._value.split('|'), *args, **kwargs)


class ConfigureMeta(type):

    def __getattr__(self, attr_name):
        return ConfigureMetaProxy(self, attr_name)


class configure(object):

    __metaclass__ = ConfigureMeta

    def __init__(self, directive, **kwargs):
        # Save execution context info
        self.frame = sys._getframe(2)

        # Map 'klass' to 'class', 'for_' to 'for, 'context' to 'for', etc:
        for from_, to in ARGUMENT_MAP.items():
            if from_ in kwargs:
                kwargs[to] = kwargs.pop(from_)
            if from_ in directive:
                directive[directive.index(from_)] = to

        # Map classes into their identifiers and concatenate lists and tuples
        # into ' ' separated strings:
        for key, value in kwargs.items():
            if type(value) in (list, tuple):
                value = [getattr(item, '__identifier__', None) or item
                         for item in value]
                kwargs[key] = ' '.join(value)
            else:
                kwargs[key] = getattr(value, '__identifier__', None) or value

        # Store processed arguments:
        self.__dict__.update(kwargs)

        # Resolve namespace and directive callable argument for decorator:
        if directive[-1] in CALLABLE_ARGUMENTS:
            if len(directive) > 2:
                ns = directive.pop(0)
                self.__dict__['namespace'] = NAMESPACES.get(ns, ns)
            else:
                self.__dict__['namespace'] = NAMESPACES.get('zope')
            self.__dict__['directive'] = directive[0]
            self.__dict__['callable'] = directive[1]

        # Or attach contextless directives immediately:
        else:
            arguments = self.__dict__.copy()
            frame = arguments.pop('frame')
            if len(directive) > 1:
                ns = directive.pop(0)
                arguments['namespace'] = NAMESPACES.get(ns, ns)
            else:
                arguments['namespace'] = NAMESPACES.get('zope')
            arguments['directive'] = directive[0]

            def callback(scanner, name, ob):
                directive_ = (arguments.pop('namespace'),
                              arguments.pop('directive'))
                with open(frame.f_code.co_filename) as source:
                    info = ParserInfo(source, frame.f_lineno, 0)
                    scanner.context.begin(directive_, arguments, info)
                    scanner.context.end()

            scope, module, f_locals, f_globals, codeinfo = \
                venusian.advice.getFrameInfo(sys._getframe(2))
            venusian.attach(module, callback, depth=2)

    def __call__(self, wrapped):
        arguments = self.__dict__.copy()
        frame = arguments.pop('frame')

        def callback(scanner, name, ob):
            name = '{0:s}.{1:s}'.format(ob.__module__, name)
            arguments[arguments.pop('callable')] = name
            directive = (arguments.pop('namespace'),
                         arguments.pop('directive'))
            with open(frame.f_code.co_filename) as source:
                info = ParserInfo(source, frame.f_lineno, 0)
                scanner.context.begin(directive, arguments, info)
                scanner.context.end()

        venusian.attach(wrapped, callback)
        return wrapped


def scan(package):
    scope, module, f_locals, f_globals, codeinfo = \
        venusian.advice.getFrameInfo(sys._getframe(1))
    venusian.attach(
        module,  # module, where scan was called
        lambda scanner, name, ob, package=package: scanner.scan(package)
    )


def i18n_domain(domain):
    scope, module, f_locals, f_globals, codeinfo = \
        venusian.advice.getFrameInfo(sys._getframe(1))
    venusian.attach(
        module,  # module, where i18n_domain was called
        lambda scanner, name, ob, domain=domain: \
        setattr(scanner.context, 'i18n_domain', domain)
    )


def venusianscan(file, context, testing=False):
    """Process a venusian scan"""

    # Set default i18n_domain
    context.i18n_domain = context.package.__name__

    # Import the given file as a module of context.package:
    name = os.path.splitext(os.path.basename(file.name))[0]
    module = imp.load_source(
        '{0:s}.{1:s}'.format(context.package.__name__, name),
        file.name
    )

    # Prepare temporary package for venusian scanner
    package = imp.new_module(module.__name__)
    setattr(package, '__configure__', module)  # Any attrname would work...

    # Execute scan!
    scanner = venusian.Scanner(context=context, testing=testing)
    scanner.scan(package)
    scanner.scan(module)


def processxmlfile(file, context, testing=False):
    """Process a configuration file (either zcml or cfg)"""
    from zope.configuration.xmlconfig import _processxmlfile
    if file.name.endswith('.py'):
        return venusianscan(file, context, testing)
    else:
        return _processxmlfile(file, context, testing)


class MonkeyPatcher(ImpLoader):
    """
    ZConfig uses PEP 302 module hooks to load this file, and this class
    implements a get_data hook to intercept the component.xml loading and give
    us a point to generate it.
    """
    def __init__(self, module):
        name = module.__name__
        path = os.path.dirname(module.__file__)
        description = ('', '', imp.PKG_DIRECTORY)
        ImpLoader.__init__(self, name, None, path, description)

    def get_data(self, pathname):
        if os.path.split(pathname) == (self.filename, 'component.xml'):
            import zope.configuration.xmlconfig
            setattr(zope.configuration.xmlconfig,
                    '_processxmlfile',
                    zope.configuration.xmlconfig.processxmlfile)
            setattr(zope.configuration.xmlconfig,
                    'processxmlfile',
                    processxmlfile)
            return '<component></component>'
        return super(MonkeyPatcher, self).get_data(self, pathname)

__loader__ = MonkeyPatcher(sys.modules[__name__])
