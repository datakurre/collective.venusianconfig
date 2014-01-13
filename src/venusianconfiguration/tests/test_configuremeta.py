# -*- coding: utf-8 -*-

import unittest


from venusianconfiguration import ConfigureMeta
from venusianconfiguration import ConfigureMetaProxy


class mock(object):

    __metaclass__ = ConfigureMeta

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ConfigureMetaTests(unittest.TestCase):

    def test_configure_traverse_creates_meta_proxy(self):
        short = mock.foo
        self.assertIsInstance(short, ConfigureMetaProxy)

    def test_configure_meta_proxy_stores_traversal_path(self):
        short = mock.foo
        self.assertEqual(short._klass, mock)
        self.assertEqual(short._value, 'foo')

    def test_configure_meta_proxy_stores_long_traversal_path(self):
        short = mock.foo.bar.foobar
        self.assertEqual(short._klass, mock)
        self.assertEqual(short._value, 'foo|bar|foobar')

    def test_configure_meta_dispatches_mock_with_traversal_path(self):
        short = mock.foo.bar.foobar()
        self.assertIsInstance(short, mock)
        self.assertIn(['foo', 'bar', 'foobar'], short.args)

    def test_configure_meta_delegates_arguments(self):
        short = mock.foo.bar.foobar(1, 2)
        self.assertIn(['foo', 'bar', 'foobar'], short.args)
        self.assertIn(1, short.args)
        self.assertIn(2, short.args)

    def test_configure_meta_delegates_keyword_arguments(self):
        short = mock.foo.bar.foobar(foo=1, bar=2)
        self.assertIn(['foo', 'bar', 'foobar'], short.args)
        self.assertDictContainsSubset({'foo': 1}, short.kwargs)
        self.assertDictContainsSubset({'bar': 2}, short.kwargs)
