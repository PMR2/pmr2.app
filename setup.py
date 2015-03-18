from setuptools import setup, find_packages
import os

version = open(os.path.join('pmr2', 'app', 'version.txt')).read().strip()

setup(
    name='pmr2.app',
    version=version,
    description='The PMR Application',
    long_description=open('README.rst').read() + "\n" +
                     open(os.path.join('docs', 'HISTORY.rst')).read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='http://www.cellml.org/',
    license='MPL, GPL, LGPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['pmr2'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Paste',
        'python-magic',
        'z3c.table>=0.6.0',
        'plone.app.content',
        'plone.browserlayer',
        'pmr2.z3cform',
        'pmr2.idgen',
        'lxml>=2.1.0',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
