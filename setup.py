from setuptools import setup, find_packages

from treemenus import __version__

setup(
    name='django-treemenus',
    version=__version__,
    description='Tree-structured menuing application for Django.',
    author='Julien Phalip',
    author_email='jphalip@gmail.com',
    url='http://github.com/jphalip/django-treemenus/',
    license='BSD',
    packages=find_packages(),
    package_data={
        'treemenus': [
            'static/img/treemenus/*.gif',
            'templates/admin/treemenus/menu/*.html',
            'templates/admin/treemenus/menuitem/*.html',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.0',
    ],
)
