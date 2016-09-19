"""Tests for lib/parsers.py

We have a few events in json format and for each we know what we are expecting.
"""
import unittest

import eccemotus.lib.parsers as P


class ParserManagerTest(unittest.TestCase):
  """Test ParserManager """
  # pylint: disable=line-too-long

  def _test_parser(self, expected_result, event):
    """Generic checks for testing a parser."""
    parsed_event = P.ParserManager.parse(event)
    for key, value in expected_result.items():
      self.assertIn(key, parsed_event)
      self.assertEqual(parsed_event[key], value, 'for key=%s' % key)

  def test_linux_utmp(self):
    """Test parser for linux:utmp:event data_type."""
    expected = {
        P.SOURCE_MACHINE_IP: '192.168.1.11',
        P.SOURCE_MACHINE_NAME: '192.168.1.11',
        P.TARGET_USER_NAME: 'dean@acserver',
        P.TARGET_MACHINE_NAME: 'acserver',
        P.TARGET_PLASO:
        'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TIMESTAMP: 1441559606244560,
    }
    self._test_parser(expected, self._linux_utmp_event)

  def test_win_evtx(self):
    """Test parser for windows:evtx:record data_type."""
    expected = {
        P.SOURCE_MACHINE_NAME: 'REGISTRAR.internal.greendale.edu',
        P.SOURCE_USER_ID: 'S-1-0-0@REGISTRAR.internal.greendale.edu',
        P.SOURCE_PLASO: 'registrar.dd/greendale_images/media/',
        P.TARGET_MACHINE_NAME: 'STUDENT-PC1',
        P.TARGET_MACHINE_IP: '192.168.1.11',
        P.TARGET_USER_ID: 'S-1-5-7@STUDENT-PC1',
        P.TARGET_USER_NAME: 'ANONYMOUS LOGON@STUDENT-PC1',
        P.TIMESTAMP: 1440409600617570,
    }
    self._test_parser(expected, self._win_evtx_event)

  def test_bsm(self):
    """Test parser for bsm:event data_type."""
    expected = {
        P.SOURCE_MACHINE_IP: '192.168.1.11',
        P.TARGET_PLASO: 'dean_mac.dd/greendale_images/media/',
        P.TARGET_USER_ID: '502@dean_mac.dd/greendale_images/media/',
        P.TARGET_USER_NAME: 'dean@dean_mac.dd/greendale_images/media/',
    }
    self._test_parser(expected, self._bsm_event)

  def test_sys_log(self):
    """Test parser for syslog:line data_type."""
    expected = {
        P.SOURCE_MACHINE_IP: '10.0.8.6',
        P.TARGET_PLASO:
        'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TARGET_USER_NAME:
        'dean@acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TIMESTAMP: 1440854525000000,
    }
    self._test_parser(expected, self._sys_log_event)

  def test_sys_log_ssh(self):
    """Test parser for syslog:ssh:login data_type."""
    expected = {
        P.SOURCE_MACHINE_IP: '10.0.8.6',
        P.TARGET_MACHINE_NAME: 'acserver',
        P.TARGET_PLASO:
        'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TARGET_USER_NAME: 'dean@acserver',
    }
    self._test_parser(expected, self._sys_log_ssh)

  # Events I am testing on. Putting them in specific tests would be too ugly.
  _linux_utmp_event = {
      '__container_type__': 'event',
      '__type__': 'AttributeContainer',
      'computer_name': '192.168.1.11',
      'data_type': 'linux:utmp:event',
      'display_name': 'TSK:/var/log/wtmp',
      'exit': 0,
      'filename': '/var/log/wtmp',
      'hostname': 'acserver',
      'inode': 0,
      'ip_address': {'__type__': 'bytes',
                     'stream': '192.168.1.11'},
      'message':
      'User: dean Computer Name: 192.168.1.11 Terminal: pts/0 PID: 16304 Terminal_ID: 808416116 Status: USER_PROCESS IP Address: 192.168.1.11 Exit: 0',
      'offset': 384,
      'parser': 'utmp',
      'pathspec': {'__type__': 'PathSpec',
                   'inode': 1073,
                   'location': '/var/log/wtmp',
                   'parent':
                   {'__type__': 'PathSpec',
                    'location': '/p1',
                    'parent':
                    {'__type__': 'PathSpec',
                     'parent':
                     {'__type__': 'PathSpec',
                      'location':
                      '/usr/local/google/home/vlejd/work/images/acserver.dd',
                      'type_indicator': 'OS'},
                     'type_indicator': 'RAW'},
                    'part_index': 2,
                    'start_offset': 1048576,
                    'type_indicator': 'TSK_PARTITION'},
                   'type_indicator': 'TSK'},
      'pid': 16304,
      'sha256_hash':
      '606ee786c85ce5e72c2438887b0734fd82fc9351ce484f48a7afe9ec1f7f2d8d',
      'status': 'USER_PROCESS',
      'store_index': 61622,
      'store_number': 2,
      'terminal': 'pts/0',
      'terminal_id': 808416116,
      'timestamp': 1441559606244560,
      'timestamp_desc': 'Start Time',
      'user': 'dean',
      'username': '-',
      'uuid': '3b3c02a3efe845df9dce368f357321b9'
  }

  _win_evtx_event = {
      '__container_type__': 'event',
      '__type__': 'AttributeContainer',
      'computer_name': 'REGISTRAR.internal.greendale.edu',
      'data_type': 'windows:evtx:record',
      'display_name': 'TSK:/Windows/System32/winevt/Logs/Security.evtx',
      'event_identifier': 4624,
      'event_level': 0,
      'filename': '/Windows/System32/winevt/Logs/Security.evtx',
      'inode': 0,
      'message_identifier': 4624,
      'offset': 0,
      'parser': 'winevtx',
      'pathspec': {'__type__': 'PathSpec',
                   'inode': 57580,
                   'location': '/Windows/System32/winevt/Logs/Security.evtx',
                   'parent': {'__type__': 'PathSpec',
                              'location': '/p2',
                              'parent':
                              {'__type__': 'PathSpec',
                               'parent':
                               {'__type__': 'PathSpec',
                                'location':
                                '/media/greendale_images/registrar.dd',
                                'type_indicator': 'OS'},
                               'type_indicator': 'RAW'},
                              'part_index': 3,
                              'start_offset': 105906176,
                              'type_indicator': 'TSK_PARTITION'},
                   'type_indicator': 'TSK'},
      'record_number': 3803,
      'sha256_hash':
      '47387ab429ebbac1ae96162143783d1f5dab692f1311fc92ec212166347f9404',
      'source_name': 'Microsoft-Windows-Security-Auditing',
      'store_index': 5610,
      'store_number': 56,
      'strings':
      ['S-1-0-0', '-', '-', '0x0000000000000000', 'S-1-5-7', 'ANONYMOUS LOGON',
       'NT AUTHORITY', '0x0000000000094a1b', '3', 'NtLmSsp ', 'NTLM',
       'STUDENT-PC1', '{00000000-0000-0000-0000-000000000000}', '-', 'NTLM V1',
       '128', '0x0000000000000000', '-', '192.168.1.11', '49192'],
      'timestamp': 1440409600617570,
      'timestamp_desc': 'Content Modification Time',
      'username': '-',
      'uuid': 'a85d856591d94678a555bda3d1efff54'
  }  # TODO(vlejd) add XML msg.

  _bsm_event = {
      '__container_type__': 'event',
      '__type__': 'AttributeContainer',
      'data_type': 'bsm:event',
      'display_name': 'TSK:/private/var/audit/20150825205628.crash_recovery',
      'event_type': 'OpenSSH login (32800)',
      'extra_tokens':
      '[BSM_TOKEN_SUBJECT32_EX: aid(502), euid(502), egid(20), uid(502), gid(20), pid(5023), session_id(5023), terminal_port(49539), terminal_ip(192.168.1.11)]. [BSM_TOKEN_TEXT: successful login dean]. [BSM_TOKEN_RETURN32: Success (0), System call status: 0]',
      'filename': '/private/var/audit/20150825205628.crash_recovery',
      'inode': 0,
      'message':
      'Type: OpenSSH login (32800) Information: [BSM_TOKEN_SUBJECT32_EX: aid(502), euid(502), egid(20), uid(502), gid(20), pid(5023), session_id(5023), terminal_port(49539), terminal_ip(192.168.1.11)]. [BSM_TOKEN_TEXT: successful login dean]. [BSM_TOKEN_RETURN32: Success (0), System call status: 0]',
      'offset': 132254,
      'parser': 'bsm_log',
      'pathspec': {'__type__': 'PathSpec',
                   'inode': 1299851,
                   'location':
                   '/private/var/audit/20150825205628.crash_recovery',
                   'parent': {'__type__': 'PathSpec',
                              'location': '/p2',
                              'parent':
                              {'__type__': 'PathSpec',
                               'parent':
                               {'__type__': 'PathSpec',
                                'location':
                                '/media/greendale_images/dean_mac.dd',
                                'type_indicator': 'OS'},
                               'type_indicator': 'RAW'},
                              'part_index': 5,
                              'start_offset': 209735680,
                              'type_indicator': 'TSK_PARTITION'},
                   'type_indicator': 'TSK'},
      'record_length': '[BSM_TOKEN_TRAILER: 97]',
      'sha256_hash':
      '440cd24ad03a6976401d759624754848ba18cd6a556a9fa319ae4a1f1994a832',
      'store_index': 54074,
      'store_number': 1,
      'timestamp': 1441559047000925,
      'timestamp_desc': 'Creation Time',
      'username': '-',
      'uuid': 'ed7ae1930c484a0da8278f6836d1d833'
  }

  _sys_log_event = {
      '__container_type__': 'event',
      '__type__': 'AttributeContainer',
      'body': 'Accepted password for dean from 10.0.8.6 port 52666 ssh2',
      'data_type': 'syslog:line',
      'display_name': 'GZIP:/var/log/auth.log.3.gz',
      'filename': '/var/log/auth.log.3.gz',
      'hostname': 'acserver',
      'inode': 0,
      'message':
      '[sshd, pid: 6686] Accepted password for dean from 10.0.8.6 port 52666 ssh2',
      'offset': 0,
      'parser': 'syslog',
      'pathspec':
      {'__type__': 'PathSpec',
       'parent': {'__type__': 'PathSpec',
                  'inode': 623,
                  'location': '/var/log/auth.log.3.gz',
                  'parent':
                  {'__type__': 'PathSpec',
                   'location':
                   '/p1',
                   'parent':
                   {'__type__': 'PathSpec',
                    'parent':
                    {'__type__': 'PathSpec',
                     'location':
                     '/usr/local/google/home/vlejd/work/images/acserver.dd',
                     'type_indicator': 'OS'},
                    'type_indicator': 'RAW'},
                   'part_index': 2,
                   'start_offset': 1048576,
                   'type_indicator': 'TSK_PARTITION'},
                  'type_indicator': 'TSK'},
       'type_indicator': 'GZIP'},
      'pid': 6686,
      'reporter': 'sshd',
      'sha256_hash':
      '61a15693f422d35cd4a22e0042e721bc1790ee878d4411a2f59052a424634ec9',
      'store_index': 62715,
      'store_number': 1,
      'timestamp': 1440854525000000,
      'timestamp_desc': 'Content Modification Time',
      'username': '-',
      'uuid': 'c21fbdaf6cb24fceac1984b160135a93'
  }

  _sys_log_ssh = {
      '__container_type__': 'event',
      '__type__': 'AttributeContainer',
      'address': '10.0.8.6',
      'authentication_method': 'publickey',
      'body':
      'Accepted publickey for dean from 10.0.8.6 port 52673 ssh2: RSA a5:ed:32:56:6e:cb:be:88:70:1d:88:4f:9b:ce:bf:d1',
      'data_type': 'syslog:ssh:login',
      'display_name': 'GZIP:/var/log/auth.log.3.gz',
      'filename': '/var/log/auth.log.3.gz',
      'fingerprint': 'RSA a5:ed:32:56:6e:cb:be:88:70:1d:88:4f:9b:ce:bf:d1',
      'hostname': 'acserver',
      'inode': 0,
      'message':
      'Successful login of user: deanfrom 10.0.8.6:52673using authentication method: publickeyssh pid: 6844',
      'offset': 0,
      'parser': 'syslog',
      'pathspec':
      {'__type__': 'PathSpec',
       'parent':
       {'__type__': 'PathSpec',
        'inode': 623,
        'location':
        '/var/log/auth.log.3.gz',
        'parent': {'__type__': 'PathSpec',
                   'location':
                   '/p1',
                   'parent':
                   {'__type__': 'PathSpec',
                    'parent':
                    {'__type__': 'PathSpec',
                     'location':
                     '/usr/local/google/home/vlejd/work/images/acserver.dd',
                     'type_indicator': 'OS'},
                    'type_indicator': 'RAW'},
                   'part_index': 2,
                   'start_offset': 1048576,
                   'type_indicator': 'TSK_PARTITION'},
        'type_indicator': 'TSK'},
       'type_indicator': 'GZIP'},
      'pid': 6844,
      'port': '52673',
      'protocol': 'ssh2',
      'reporter': 'sshd',
      'sha256_hash':
      '61a15693f422d35cd4a22e0042e721bc1790ee878d4411a2f59052a424634ec9',
      'store_index': 62745,
      'store_number': 1,
      'timestamp': 1440854809000000,
      'timestamp_desc': 'Content Modification Time',
      'username': 'dean',
      'uuid': '090d45a7d0ad458ab1937b0982dbedf4'
  }
