from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('treemenus'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[10:] # Strip "treemenus/" or "treemenus\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='treemenus',
      version='0.0',
      description='Tree-like menuing application for Django',
      author='Julien Phalip',
      author_email='jipedev@gmail.com',
      url='http://code.google.com/p/django-treemenus/',
      package_dir={'treemenus': 'treemenus'},
      packages=packages,
      package_data={'treemenus': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
