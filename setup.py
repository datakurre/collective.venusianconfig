from setuptools import setup, find_packages

setup(
    name='venusianconfiguration',
    version='0.9.0',
    description='Experiment for configuring with venusian instead of *.zcml',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.txt').read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/datakurre/collective.venusianconfig/',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.configuration',
        'venusian>=1.0a8',
    ],
    extras_require={'test': [
        'plone.testing',
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
