from setuptools import setup, find_packages

setup(
    name='django-treemenus',
    version='0.8.5',
    description='Tree-like menuing application for Django.',
    author='Julien Phalip',
    author_email='julien@julienphalip.com',
    url='http://code.google.com/p/django-treemenus/',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)