#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to run the tests."""

import unittest
import sys


if __name__ == u'__main__':
  test_suite = unittest.TestLoader().discover(u'eccemotus/tests',
                                              pattern=u'*.py')
  test_results = unittest.TextTestRunner(verbosity=2).run(test_suite)
  if not test_results.wasSuccessful():
    sys.exit(1)

  test_suite = unittest.TestLoader().discover(u'eccemotus/',
                                              pattern=u'*_test.py')
  test_results = unittest.TextTestRunner(verbosity=2).run(test_suite)
  if not test_results.wasSuccessful():
    sys.exit(1)
