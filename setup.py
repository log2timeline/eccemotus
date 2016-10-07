#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This is the setup file for the project. The standard setup rules apply:

   python setup.py build
   sudo python setup.py install
"""

from setuptools import find_packages, setup


eccemotus_description = (
    u'Eccemotus library for extracting and visualizing information about '
    u'lateral movement out of plaso event logs. It consists of three parts '
    u'Library on its own which contains tools for parsing an managing '
    u'information extracted from logs, command line interface for this library '
    u'and web interface with interactive javascript visualization.')

setup(
    name=u'eccemotus',
    version=u'2016.10',
    description=u'Lateral movement explorer',
    long_description=eccemotus_description,
    license=u'Apache License, Version 2.0',
    url=u'http://www.timesketch.org/',
    maintainer=u'Eccemotus development team',
    maintainer_email=u'eccemotus-dev@googlegroups.com',
    scripts=frozenset([
        u'eccemotus_console.py',
        u'eccemotus_web.py']),
    classifiers=[
        u'Development Status :: 4 - Beta',
        u'Environment :: Web Environment',
        u'Operating System :: OS Independent',
        u'Programming Language :: Python',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        u'elastic':[u'elasticsearch'],
        u'web':[u'Flask'],
    }
)
