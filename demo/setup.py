from setuptools import setup, find_packages

setup(
    name='venusianconfigdemo',
    version='1.0.0',
    description='Demonstration of collective.venusianconfig',
    long_description=(open('README.txt').read() + '\n' +
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
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.venusianconfig',
    ],
    extras_require={'test': [
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
