# -*- coding: utf-8 -*-
"""Tests for utils."""

import unittest

from eccemotus.lib.parsers import utils


class UtilsTest(unittest.TestCase):
  """Tests for utils."""

  def test_FirstTrue(self):
    """Tests extracting object from list that evaluates to True."""

    first_true = utils.FirstTrue([None, u'', {}, u'true'])
    expected_first_true = u'true'
    self.assertEqual(first_true, expected_first_true)

    first_true = utils.FirstTrue([None, u'', {}])
    expected_first_true = None
    self.assertIs(first_true, expected_first_true)

    first_true = utils.FirstTrue([None, u'', {}], u'true')
    expected_first_true = u'true'
    self.assertEqual(first_true, expected_first_true)


  def test_GetImageName(self):
    """Tests extracting plaso source file name from pathspec dictionary."""

    event = {
        u'pathspec': {
            u'__type__': u'PathSpec',
            u'inode': 1073,
            u'location': u'/var/log/wtmp',
            u'parent': {
                u'__type__': u'PathSpec',
                u'location': u'/p1',
                u'parent': {
                    u'__type__': u'PathSpec',
                    u'parent': {
                        u'__type__': u'PathSpec',
                        u'location': u'/home/user/images/image.dd',
                        u'type_indicator': u'OS'},
                    u'type_indicator': u'RAW'},
                u'part_index': 2,
                u'start_offset': 1048576,
                u'type_indicator': u'TSK_PARTITION'},
            u'type_indicator': u'TSK'},
    }
    plaso_file_name = utils.GetImageName(event)
    expected_plso_file_name = u'image.dd/images/user/home/'
    self.assertEqual(plaso_file_name, expected_plso_file_name)
