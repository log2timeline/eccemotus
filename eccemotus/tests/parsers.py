# -*- coding: utf-8 -*-
"""Tests for parsers."""

import unittest

from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import utils


class ParserManagerTest(unittest.TestCase):
  """Test ParserManager """
  # pylint: disable=line-too-long

  def _testParser(self, expected_result, event):
    """Generic checks for testing a parser.

    Args:
      expected_result (dict): expected result of parsing.
      event (dict): dict serialized plaso event.
    """
    parsed_event = manager.ParserManager.Parse(event)
    for key, value in expected_result.items():
      self.assertIn(key, parsed_event)
      self.assertEqual(parsed_event[key], value)

  def test_LinuxUtmp(self):
    """Test parser for linux:utmp:event data_type."""
    expected = {
        utils.SOURCE_MACHINE_IP: u'192.168.1.11',
        utils.SOURCE_MACHINE_NAME: u'192.168.1.11',
        utils.TARGET_USER_NAME: u'dean@acserver',
        utils.TARGET_MACHINE_NAME: u'acserver',
        utils.TARGET_PLASO:
        u'acserver.dd/images/user/usr/',
        utils.TIMESTAMP: 1441559606244560,
    }
    self._testParser(expected, self._linux_utmp_event)

  def test_WinEvtx(self):
    """Test parser for windows:evtx:record data_type."""
    expected = {
        utils.SOURCE_MACHINE_NAME: u'REGISTRAR.internal.greendale.edu',
        utils.SOURCE_USER_ID: u'S-1-0-0@REGISTRAR.internal.greendale.edu',
        utils.SOURCE_PLASO: u'registrar.dd/greendale_images/media/',
        utils.TARGET_MACHINE_NAME: u'STUDENT-PC1',
        utils.TARGET_MACHINE_IP: u'192.168.1.11',
        utils.TARGET_USER_ID: u'S-1-5-7@STUDENT-PC1',
        utils.TARGET_USER_NAME: u'ANONYMOUS LOGON@STUDENT-PC1',
        utils.TIMESTAMP: 1440409600617570,
    }
    self._testParser(expected, self._win_evtx_event)

  def test_Bsm(self):
    """Test parser for bsm:event data_type."""
    expected = {
        utils.SOURCE_MACHINE_IP: u'192.168.1.11',
        utils.TARGET_PLASO: u'dean_mac.dd/greendale_images/media/',
        utils.TARGET_USER_ID: u'502@dean_mac.dd/greendale_images/media/',
        utils.TARGET_USER_NAME: u'dean@dean_mac.dd/greendale_images/media/',
    }
    self._testParser(expected, self._bsm_event)

  def test_SysLog(self):
    """Test parser for syslog:line data_type."""
    expected = {
        utils.SOURCE_MACHINE_IP: u'10.0.8.6',
        utils.TARGET_PLASO:
        u'acserver.dd/images/user/usr/',
        utils.TARGET_USER_NAME:
        u'dean@acserver.dd/images/user/usr/',
        utils.TIMESTAMP: 1440854525000000,
    }
    self._testParser(expected, self._sys_log_event)

  def test_SysLogSsh(self):
    """Test parser for syslog:ssh:login data_type."""
    expected = {
        utils.SOURCE_MACHINE_IP: u'10.0.8.6',
        utils.TARGET_MACHINE_NAME: u'acserver',
        utils.TARGET_PLASO:
        u'acserver.dd/images/user/usr/',
        utils.TARGET_USER_NAME: u'dean@acserver',
    }
    self._testParser(expected, self._sys_log_ssh)

  # Events I am testing on. Putting them in specific tests would be too ugly.
  # Proper formating would not be very readable.
  _linux_utmp_event = {
      u'__container_type__': u'event',
      u'__type__': u'AttributeContainer',
      u'computer_name': u'192.168.1.11',
      u'data_type': u'linux:utmp:event',
      u'display_name': u'TSK:/var/log/wtmp',
      u'exit': 0,
      u'filename': u'/var/log/wtmp',
      u'hostname': u'acserver',
      u'inode': 0,
      u'ip_address': {u'__type__': u'bytes',
                      u'stream': u'192.168.1.11'},
      u'message':
      u'User: dean Computer Name: 192.168.1.11 Terminal: pts/0 PID: 16304 Terminal_ID: 808416116 Status: USER_PROCESS IP Address: 192.168.1.11 Exit: 0',
      u'offset': 384,
      u'parser': u'utmp',
      u'pathspec': {u'__type__': u'PathSpec',
                    u'inode': 1073,
                    u'location': u'/var/log/wtmp',
                    u'parent':
                    {u'__type__': u'PathSpec',
                     u'location': u'/p1',
                     u'parent':
                     {u'__type__': u'PathSpec',
                      u'parent':
                      {u'__type__': u'PathSpec',
                       u'location':
                       u'/usr/user/images/acserver.dd',
                       u'type_indicator': u'OS'},
                      u'type_indicator': u'RAW'},
                     u'part_index': 2,
                     u'start_offset': 1048576,
                     u'type_indicator': u'TSK_PARTITION'},
                    u'type_indicator': u'TSK'},
      u'pid': 16304,
      u'sha256_hash':
      u'606ee786c85ce5e72c2438887b0734fd82fc9351ce484f48a7afe9ec1f7f2d8d',
      u'status': u'USER_PROCESS',
      u'store_index': 61622,
      u'store_number': 2,
      u'terminal': u'pts/0',
      u'terminal_id': 808416116,
      u'timestamp': 1441559606244560,
      u'timestamp_desc': u'Start Time',
      u'user': u'dean',
      u'username': u'-',
      u'uuid': u'3b3c02a3efe845df9dce368f357321b9'
  }

  _win_evtx_event = {
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
      u'pathspec': {u'__type__': u'PathSpec',
                    u'inode': 57580,
                    u'location': u'/Windows/System32/winevt/Logs/Security.evtx',
                    u'parent': {u'__type__': u'PathSpec',
                                u'location': u'/p2',
                                u'parent':
                                {u'__type__': u'PathSpec',
                                 u'parent':
                                 {u'__type__': u'PathSpec',
                                  u'location':
                                  u'/media/greendale_images/registrar.dd',
                                  u'type_indicator': u'OS'},
                                 u'type_indicator': u'RAW'},
                                u'part_index': 3,
                                u'start_offset': 105906176,
                                u'type_indicator': u'TSK_PARTITION'},
                    u'type_indicator': u'TSK'},
      u'record_number': 3803,
      u'sha256_hash':
      u'47387ab429ebbac1ae96162143783d1f5dab692f1311fc92ec212166347f9404',
      u'source_name': u'Microsoft-Windows-Security-Auditing',
      u'store_index': 5610,
      u'store_number': 56,
      u'strings':
      [u'S-1-0-0', u'-', u'-', u'0x0000000000000000', u'S-1-5-7', u'ANONYMOUS LOGON',
       u'NT AUTHORITY', u'0x0000000000094a1b', u'3', u'NtLmSsp ', u'NTLM',
       u'STUDENT-PC1', '{00000000-0000-0000-0000-000000000000}', u'-', u'NTLM V1',
       u'128', u'0x0000000000000000', u'-', u'192.168.1.11', u'49192'],
      u'timestamp': 1440409600617570,
      u'timestamp_desc': u'Content Modification Time',
      u'username': u'-',
      u'uuid': u'a85d856591d94678a555bda3d1efff54'
  }

  _bsm_event = {
      u'__container_type__': u'event',
      u'__type__': u'AttributeContainer',
      u'data_type': u'bsm:event',
      u'display_name': u'TSK:/private/var/audit/20150825205628.crash_recovery',
      u'event_type': u'OpenSSH login (32800)',
      u'extra_tokens':
      u'[BSM_TOKEN_SUBJECT32_EX: aid(502), euid(502), egid(20), uid(502), gid(20), pid(5023), session_id(5023), terminal_port(49539), terminal_ip(192.168.1.11)]. [BSM_TOKEN_TEXT: successful login dean]. [BSM_TOKEN_RETURN32: Success (0), System call status: 0]',
      u'filename': u'/private/var/audit/20150825205628.crash_recovery',
      u'inode': 0,
      u'message':
      u'Type: OpenSSH login (32800) Information: [BSM_TOKEN_SUBJECT32_EX: aid(502), euid(502), egid(20), uid(502), gid(20), pid(5023), session_id(5023), terminal_port(49539), terminal_ip(192.168.1.11)]. [BSM_TOKEN_TEXT: successful login dean]. [BSM_TOKEN_RETURN32: Success (0), System call status: 0]',
      u'offset': 132254,
      u'parser': u'bsm_log',
      u'pathspec': {u'__type__': u'PathSpec',
                    u'inode': 1299851,
                    u'location':
                    u'/private/var/audit/20150825205628.crash_recovery',
                    u'parent': {u'__type__': u'PathSpec',
                                u'location': u'/p2',
                                u'parent':
                                {u'__type__': u'PathSpec',
                                 u'parent':
                                 {u'__type__': u'PathSpec',
                                  u'location':
                                  u'/media/greendale_images/dean_mac.dd',
                                  u'type_indicator': u'OS'},
                                 u'type_indicator': u'RAW'},
                                u'part_index': 5,
                                u'start_offset': 209735680,
                                u'type_indicator': u'TSK_PARTITION'},
                    u'type_indicator': u'TSK'},
      u'record_length': u'[BSM_TOKEN_TRAILER: 97]',
      u'sha256_hash':
      u'440cd24ad03a6976401d759624754848ba18cd6a556a9fa319ae4a1f1994a832',
      u'store_index': 54074,
      u'store_number': 1,
      u'timestamp': 1441559047000925,
      u'timestamp_desc': u'Creation Time',
      u'username': u'-',
      u'uuid': u'ed7ae1930c484a0da8278f6836d1d833'
  }

  _sys_log_event = {
      u'__container_type__': u'event',
      u'__type__': u'AttributeContainer',
      u'body': u'Accepted password for dean from 10.0.8.6 port 52666 ssh2',
      u'data_type': u'syslog:line',
      u'display_name': u'GZIP:/var/log/auth.log.3.gz',
      u'filename': u'/var/log/auth.log.3.gz',
      u'hostname': u'acserver',
      u'inode': 0,
      u'message':
      u'[sshd, pid: 6686] Accepted password for dean from 10.0.8.6 port 52666 ssh2',
      u'offset': 0,
      u'parser': u'syslog',
      u'pathspec':
      {u'__type__': u'PathSpec',
       u'parent': {u'__type__': u'PathSpec',
                   u'inode': 623,
                   u'location': u'/var/log/auth.log.3.gz',
                   u'parent':
                   {u'__type__': u'PathSpec',
                    u'location':
                    u'/p1',
                    u'parent':
                    {u'__type__': u'PathSpec',
                     u'parent':
                     {u'__type__': u'PathSpec',
                      u'location':
                      u'/usr/user/images/acserver.dd',
                      u'type_indicator': u'OS'},
                     u'type_indicator': u'RAW'},
                    u'part_index': 2,
                    u'start_offset': 1048576,
                    u'type_indicator': u'TSK_PARTITION'},
                   u'type_indicator': u'TSK'},
       u'type_indicator': u'GZIP'},
      u'pid': 6686,
      u'reporter': u'sshd',
      u'sha256_hash':
      u'61a15693f422d35cd4a22e0042e721bc1790ee878d4411a2f59052a424634ec9',
      u'store_index': 62715,
      u'store_number': 1,
      u'timestamp': 1440854525000000,
      u'timestamp_desc': u'Content Modification Time',
      u'username': u'-',
      u'uuid': u'c21fbdaf6cb24fceac1984b160135a93'
  }

  _sys_log_ssh = {
      u'__container_type__': u'event',
      u'__type__': u'AttributeContainer',
      u'address': u'10.0.8.6',
      u'authentication_method': u'publickey',
      u'body':
      u'Accepted publickey for dean from 10.0.8.6 port 52673 ssh2: RSA a5:ed:32:56:6e:cb:be:88:70:1d:88:4f:9b:ce:bf:d1',
      u'data_type': u'syslog:ssh:login',
      u'display_name': u'GZIP:/var/log/auth.log.3.gz',
      u'filename': u'/var/log/auth.log.3.gz',
      u'fingerprint': u'RSA a5:ed:32:56:6e:cb:be:88:70:1d:88:4f:9b:ce:bf:d1',
      u'hostname': u'acserver',
      u'inode': 0,
      u'message':
      u'Successful login of user: deanfrom 10.0.8.6:52673using authentication method: publickeyssh pid: 6844',
      u'offset': 0,
      u'parser': u'syslog',
      u'pathspec':
      {u'__type__': u'PathSpec',
       u'parent':
       {u'__type__': u'PathSpec',
        u'inode': 623,
        u'location':
        u'/var/log/auth.log.3.gz',
        u'parent': {u'__type__': u'PathSpec',
                    u'location':
                    u'/p1',
                    u'parent':
                    {u'__type__': u'PathSpec',
                     u'parent':
                     {u'__type__': u'PathSpec',
                      u'location':
                      u'/usr/user/images/acserver.dd',
                      u'type_indicator': u'OS'},
                     u'type_indicator': u'RAW'},
                    u'part_index': 2,
                    u'start_offset': 1048576,
                    u'type_indicator': u'TSK_PARTITION'},
        u'type_indicator': u'TSK'},
       u'type_indicator': u'GZIP'},
      u'pid': 6844,
      u'port': u'52673',
      u'protocol': u'ssh2',
      u'reporter': u'sshd',
      u'sha256_hash':
      u'61a15693f422d35cd4a22e0042e721bc1790ee878d4411a2f59052a424634ec9',
      u'store_index': 62745,
      u'store_number': 1,
      u'timestamp': 1440854809000000,
      u'timestamp_desc': u'Content Modification Time',
      u'username': u'dean',
      u'uuid': u'090d45a7d0ad458ab1937b0982dbedf4'
  }
