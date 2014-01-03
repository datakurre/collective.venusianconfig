# -*- coding: utf-8 -*-
from pkgutil import ImpLoader

import imp
import os
import re
import sys

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.xmlconfig import ParserInfo
from zope.configuration.xmlconfig import ConfigurationHandler

import venusian


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


CONFIGURE_START = re.compile('^\s*@?configure.*')
CONFIGURE_END = re.compile('.*\)\s*$')


class CodeInfo(ParserInfo):

    def __init__(self, frame):
        file_ = frame.f_code.co_filename
        line = frame.f_lineno
        super(CodeInfo, self).__init__(file_, line, 0)

    def __str__(self):
        if self.line == self.eline and self.column == self.ecolumn:
            try:
                with open(self.file) as file_:
                    lines = file_.readlines()
                    self.line + 1  # fix to start scan below the directive
                    while self.line > 0:
                        if not CONFIGURE_START.match(lines[self.line - 1]):
                            self.line -= 1
                            continue
                        break
                    while self.eline < len(lines):
                        if not CONFIGURE_END.match(lines[self.eline - 1]):
                            self.eline += 1
                            continue
                        self.ecolumn = len(lines[self.eline - 1])
                        break
            except IOError:
                pass  # let the super call to raise this exception
        return super(CodeInfo, self).__str__()


def get_identifier_or_string(value):
    if hasattr(value, '__module__') and hasattr(value, '__name__'):
        return '.'.join([value.__module__, value.__name__])
    elif (hasattr(value, '__package__') and hasattr(value, '__name__')
          and value.__package__ == value.__name__):
        return value.__name__
    else:
        return value


class configure(object):

    __metaclass__ = ConfigureMeta

    def __enter__(self):
        # Set complex-flag to mark begin of nested directive
        self.__is_complex__ = True
        return self.__class__

    def __exit__(self, type, value, tb):
        # Register context end to end nested directive
        def callback(scanner, name, ob):
            scanner.context.end()

        if tb is None:
            # Look up first frame outside this file
            depth = 0
            while __file__.startswith(sys._getframe(depth).f_code.co_filename):
                depth += 1
            # Register the callback
            scope, module, f_locals, f_globals, codeinfo = \
                venusian.advice.getFrameInfo(sys._getframe(depth))
            venusian.attach(module, callback, depth=depth)

    def __init__(self, directive=['zope', 'configure'], **kwargs):
        # Flag whether this is a complex (nested) directive or not
        self.__is_complex__ = False

        # Look up first frame outside this file
        self.__depth__ = 0
        while __file__.startswith(
                sys._getframe(self.__depth__).f_code.co_filename):
            self.__depth__ += 1

        # Save execution context info
        self.__info__ = CodeInfo(sys._getframe(self.__depth__))

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
                value = map(get_identifier_or_string, value)
                kwargs[key] = ' '.join(value)
            else:
                kwargs[key] = get_identifier_or_string(value)

        # Store processed arguments:
        self.__arguments__ = kwargs.copy()

        # Resolve namespace and directive callable argument for decorator:
        if directive[-1] in CALLABLE_ARGUMENTS:
            if len(directive) > 2:
                ns = directive.pop(0)
                self.__arguments__['namespace'] = NAMESPACES.get(ns, ns)
            else:
                self.__arguments__['namespace'] = NAMESPACES.get('zope')
            self.__arguments__['directive'] = directive[0]
            self.__arguments__['callable'] = directive[1]

        # Or attach contextless directives immediately:
        else:
            arguments = self.__arguments__.copy()
            if len(directive) > 1:
                ns = directive.pop(0)
                arguments['namespace'] = NAMESPACES.get(ns, ns)
            else:
                arguments['namespace'] = NAMESPACES.get('zope')
            arguments['directive'] = directive[0]

            arguments['__self__'] = self

            def callback(scanner, name, ob):
                # Evaluate conditions
                handler = ConfigurationHandler(scanner.context,
                                               testing=scanner.testing)
                condition = arguments.pop('condition', None)
                if condition and not handler.evaluateCondition(condition):
                    return

                # Configure standalone directive
                directive_ = (arguments.pop('namespace'),
                              arguments.pop('directive'))
                self_ = arguments.pop('__self__')
                scanner.context.begin(directive_, arguments, self_.__info__)

                # Do not end when used with 'with' statement
                if not self_.__is_complex__:
                    scanner.context.end()

            scope, module, f_locals, f_globals, codeinfo = \
                venusian.advice.getFrameInfo(sys._getframe(self.__depth__))
            venusian.attach(module, callback, depth=self.__depth__)

    def __call__(self, wrapped):
        arguments = self.__arguments__.copy()
        arguments['__self__'] = self

        def callback(scanner, name, ob):
            # Evaluate conditions
            handler = ConfigurationHandler(scanner.context,
                                           testing=scanner.testing)
            condition = arguments.pop('condition', None)
            if condition and not handler.evaluateCondition(condition):
                return

            # Configure standalone directive
            name = '{0:s}.{1:s}'.format(ob.__module__, name)
            arguments[arguments.pop('callable')] = name
            directive = (arguments.pop('namespace'),
                         arguments.pop('directive'))
            self_ = arguments.pop('__self__')
            scanner.context.begin(directive, arguments, self_.__info__)
            scanner.context.end()

        venusian.attach(wrapped, callback)
        return wrapped


def _scan(scanner, package, force=False):
    # Check for scanning of sub-packages, which is not yet supported:
    if not os.path.dirname(scanner.context.package.__file__) == \
            os.path.dirname(package.__file__):
        package_dirname = os.path.dirname(package.__file__)
        raise ConfigurationError(
            "Cannot scan package '{0}'. ".format(package_dirname) +
            "Only modules in the same package can be scanned. "
            "Sub-packages or separate packages must be configured "
            "using include-directive."
        )

    if force or scanner.context.processFile(package.__file__):
        # Scan non-decorator configure-calls:
        _package = imp.new_module(package.__name__)
        setattr(_package, '__configure__', package)  # Any name would work...
        scanner.scan(_package)

        # Scan decorators:
        scanner.scan(package)


def scan(package):
    """Scan the package for registered venusian callbacks"""
    scope, module, f_locals, f_globals, codeinfo = \
        venusian.advice.getFrameInfo(sys._getframe(1))
    venusian.attach(
        module,  # module, where scan was called
        lambda scanner, name, ob, package=package: _scan(scanner, package)
    )


def i18n_domain(domain):
    """Set i18n domain for the current context"""
    scope, module, f_locals, f_globals, codeinfo = \
        venusian.advice.getFrameInfo(sys._getframe(1))
    venusian.attach(
        module,  # module, where i18n_domain was called
        lambda scanner, name, ob, domain=domain:
        setattr(scanner.context, 'i18n_domain', domain)
    )


def venusianscan(file, context, testing=False, force=False):
    """Process a venusian scan"""

    # Set default i18n_domain
    context.i18n_domain = context.package.__name__

    # Import the given file as a module of context.package:
    name = os.path.splitext(os.path.basename(file.name))[0]
    package = imp.load_source(
        '{0:s}.{1:s}'.format(context.package.__name__, name),
        file.name
    )

    # Initialize scanner
    scanner = venusian.Scanner(context=context, testing=testing)

    # Scan the package
    _scan(scanner, package, force=force)


def processxmlfile(file, context, testing=False):
    """Process a configuration file (either zcml or cfg)"""
    from zope.configuration.xmlconfig import _processxmlfile
    if file.name.endswith('.py'):
        return venusianscan(file, context, testing, force=True)
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
