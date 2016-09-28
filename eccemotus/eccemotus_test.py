# -*- coding: utf-8 -*-
"""Tests for eccemotus.py"""

import unittest
import eccemotus.eccemotus_lib as E

class EccemotusTest(unittest.TestCase):
  """Test eccemotus."""

  def test_CreateGraph(self):
    """Test CreateGraph."""
    event = {
        u'__container_type__': u'event',
        u'__type__': u'AttributeContainer',
        u'computer_name': u'REGISTRAR.internal.greendale.edu',
        u'data_type': u'windows:evtx:record',
        u'display_name': u'TSK:/Windows/System32/winevt/Logs/Security.evtx',
        u'event_identifier': 4624,
        u'event_level': 0,
        u'filename': u'/Windows/System32/winevt/Logs/Security.evtx',
        u'inode': 0,
        u'message_identifier': 4624,
        u'offset': 0,
        u'parser': u'winevtx',
        u'pathspec': {
            u'location': u'/media/greendale_images/registrar.dd'},
        u'record_number': 3803,
        u'sha256_hash':
        u'47387ab429ebbac1ae96162143783d1f5dab692f1311fc92ec212166347f9404',
        u'source_name': u'Microsoft-Windows-Security-Auditing',
        u'store_index': 5610,
        u'store_number': 56,
        u'strings': [
            u'S-1-0-0', u'-', u'-', u'0x0000000000000000', u'S-1-5-7',
            u'ANONYMOUS LOGON', u'NT AUTHORITY', u'0x0000000000094a1b', u'3',
            u'NtLmSsp ', u'NTLM', u'STUDENT-PC1',
            u'{00000000-0000-0000-0000-000000000000}', u'-', u'NTLM V1',
            u'128', u'0x0000000000000000', u'-', u'192.168.1.11', u'49192'],
        u'timestamp': 1440409600617570,
        u'timestamp_desc': u'Content Modification Time',
        u'username': u'-',
        u'uuid': u'a85d856591d94678a555bda3d1efff54'
    }
    graph = E.GetGraph([event])
    self.assertEqual(len(graph.nodes), 6)
    self.assertEqual(len(graph.edges), 8)

