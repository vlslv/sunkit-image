#!/usr/bin/env python
# This file is based havily on the astropy version here:
# https://github.com/astropy/package-template/blob/master/setup.py
# Which is licensed under the astropy license, see licenses/ASTROPY.rst.

################################################################################
###### YOU SHOULD NOT HAVE TO EDIT THIS FILE, YOU SHOULD EDIT setup.cfg. #######
################################################################################
# Note: This file needs to be Python 2 / <3.6 compatible, so that the nice
# "sunkit-image only supports Python 3.6+" error prints without syntax errors etc.

import os
import sys
import glob
import builtins  # noqa
import itertools

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

# Get some values from the setup.cfg
conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'sunkit_image')
DESCRIPTION = metadata.get('description', 'sunkit_image: Solar Physics image analysis')
AUTHOR = metadata.get('author', 'The SunPy Community')
AUTHOR_EMAIL = metadata.get('author_email', '')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'https://sunpy.org')
__minimum_python_version__ = metadata.get("minimum_python_version", "3.6")

# Enforce Python version check - this is the same check as in __init__.py but
# this one has to happen before importing ah_bootstrap.
if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    sys.stderr.write("ERROR: sunkit-image requires Python {} or later\n".format(__minimum_python_version__))
    sys.exit(1)

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Import ah_bootstrap after the python version validation
import ah_bootstrap  # noqa
from setuptools import setup  # noqa
from astropy_helpers.git_helpers import get_git_devstr  # noqa
from astropy_helpers.setup_helpers import get_package_info  # noqa
from astropy_helpers.setup_helpers import get_debug_option, register_commands
from astropy_helpers.version_helpers import generate_version_py  # noqa

builtins._SUNPY_SETUP_ = True


# -- Read the Docs Setup  -----------------------------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    os.environ['HOME'] = '/home/docs/'
    os.environ['SUNPY_CONFIGDIR'] = '/home/docs/'

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
# This is used by get_pkg_data in astropy amongst other things
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP440 compatible (http://www.python.org/dev/peps/pep-0440)
VERSION = metadata.get('version', '0.0.dev0')

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behaviour.
cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)

try:
    from sunpy.tests.setup_command import SunPyTest
    # Overwrite the Astropy Testing framework
    cmdclassd['test'] = type('SunPyTest', (SunPyTest,),
                             {'package_name': 'sunkit-image'})

except Exception:
    # Catch everything, if it doesn't work, we still want SunPy to install.
    pass

# Freeze build information in version.py
generate_version_py(PACKAGENAME, VERSION, RELEASE,
                    get_debug_option(PACKAGENAME))

# Treat everything in scripts except README* as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if not os.path.basename(fname).startswith('README')]


# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])
package_info['package_data'][PACKAGENAME].append('data/*')

# Define entry points for command-line scripts
entry_points = {'console_scripts': []}

if conf.has_section('entry_points'):
    entry_point_list = conf.items('entry_points')
    for entry_point in entry_point_list:
        entry_points['console_scripts'].append('{0} = {1}'.format(
            entry_point[0], entry_point[1]))

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)


extra_tags = [m.strip() for m in metadata.get("extra_requires", "").split(',')]
if extra_tags:
    extras_require = {tag: [m.strip() for m in metadata["{tag}_requires".format(tag=tag)].split(',')]
                      for tag in extra_tags}
    extras_require['all'] = list(itertools.chain.from_iterable(extras_require.values()))
else:
    extras_require = None

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      scripts=scripts,
      setup_requires=[s.strip() for s in metadata.get("setup_requires", "").split(',')],
      install_requires=[s.strip() for s in metadata['install_requires'].split(',')],
      extras_require=extras_require,
      tests_require=extras_require.get("all", ""),
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      project_urls={'Funding': 'https://www.flipcause.com/widget/widget_home/MTgxMTU=',
                    'Source': 'https://github.com/sunpy/sunkit-image/',
                    'Tracker': 'https://github.com/sunpy/sunkit-image/issues'
                    },
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/x-rst',
      cmdclass=cmdclassd,
      zip_safe=False,
      entry_points=entry_points,
      python_requires='>={}'.format(__minimum_python_version__),
      include_package_data=True,
      **package_info
      )
