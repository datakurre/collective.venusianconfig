# -*- coding: utf-8 -*-
import imp
import os
import sys
import venusian
from pkgutil import ImpLoader

NAMESPACES = {
    '': 'http://namespaces.zope.org/zope',
    'meta': 'http://namespaces.zope.org/meta',
    'zcml': 'http://namespaces.zope.org/zcml',
    'grok': 'http://namespaces.zope.org/grok',
    'browser': 'http://namespaces.zope.org/browser',
    'genericsetup': 'http://namespaces.zope.org/genericsetup',
    'i18n': 'http://namespaces.zope.org/i18n'
}

ARGUMENT_MAP = {
    'context': 'for'
}


class configure(object):

    def __init__(self, directive, **kwargs):
        # Map 'context' to 'for', etc:
        for from_, to in ARGUMENT_MAP.items():
            if from_ in kwargs:
                kwargs[to] = kwargs.pop(from_)

        # Concatenate lists and tuples into ' ' separated strings:
        for key, value in kwargs.items():
            if type(value) in (list, tuple):
                kwargs[key] = ' '.join(value)

        # Store arguments:
        self.__dict__.update(kwargs)

        # Resolve namespace and directive callable argument:
        parts = directive.split(':')
        assert len(parts) > 1 and len(parts) < 4, \
            ('{0:s} should look like '
             '[namespace:]directive:argument').format(directive)
        if len(parts) > 2:
            self.__dict__['namespace'] = NAMESPACES[parts.pop(0)]
        else:
            self.__dict__['namespace'] = NAMESPACES['']
        self.__dict__['directive'] = parts[0]
        self.__dict__['callable'] = parts[1]

    def __call__(self, wrapped):
        arguments = self.__dict__.copy()

        def callback(scanner, name, ob):
            name = '{0:s}.{1:s}'.format(ob.__module__, name)
            arguments[arguments.pop('callable')] = name
            directive = (arguments.pop('namespace'),
                         arguments.pop('directive'))
            scanner.context.begin(directive, arguments)
            scanner.context.end()

        venusian.attach(wrapped, callback)
        return wrapped


def venusianscan(file, context, testing=False):
    """Process a venusian scan"""
    scanner = venusian.Scanner(context=context, testing=testing)

    seen = set(sys.modules.keys())
    filename = os.path.splitext(os.path.basename(file.name))[0]
    imp.load_source('{0:s}.{1:s}'.format(context.package.__name__, filename),
                    file.name)
    loaded = set(sys.modules.keys()).difference(seen)

    for name in loaded:
        if name.startswith(context.package.__name__):
            module = sys.modules[name]
            if module:
                scanner.scan(module)


def processxmlfile(file, context, testing=False):
    """Process a configuration file (either zcml or cfg)"""
    from zope.configuration.xmlconfig import _processxmlfile
    if file.name.endswith('.zcml'):
        return _processxmlfile(file, context, testing)
    else:
        return venusianscan(file, context, testing)


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
