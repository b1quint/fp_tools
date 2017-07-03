# -*- coding: utf-8 -*-
"""
A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


# Always prefer setuptools over distutils
from setuptools import setup

from fp_tools.version import api, feature, bug

setup(
    name='fp_tools',
    version='%d.%d.%d' % (api, feature, bug),
    description='Some tools to handle FP data',
    url='https://b1quint.github.io/fp_tools',
    author='Bruno Quint',
    author_email='bquint@ctio.noao.edu',
    license='3-clause BSD License',
    packages=['fp_tools'],
    package_dir={'fp_tools': 'fp_tools'},
    # package_data={},
    scripts=['scripts/fp_cut', 'scripts/fp_repeat'],
    zip_safe=False,
)