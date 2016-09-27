# -*- coding: utf-8 -*-
"""Provides way for parsing remote access related information from plaso logs.

Use ParserManager.Parse(event) and it will extract interesting fields in context
of lateral movement from plaso event.
"""
from __future__ import print_function
import json
import re
import sys
import traceback

# Canonical names for interesting information (fields).
EVENT_ID = u'event_id'
TIMESTAMP = u'timestamp'

SOURCE_MACHINE_IP = u'source:ip'
SOURCE_MACHINE_NAME = u'source:machine_name'
SOURCE_PLASO = u'source:plaso'
SOURCE_USER_ID = u'source:user_id'
SOURCE_USER_NAME = u'source:user_name'

TARGET_MACHINE_IP = u'target:ip'
TARGET_MACHINE_NAME = u'target:machine_name'
TARGET_PLASO = u'target:plaso'
TARGET_USER_ID = u'target:user_id'
TARGET_USER_NAME = u'target:user_name'

# Black lists for common invalid or uninteresting field values.
BASIC_BLACK_LIST = {
    u'ip': [u'127.0.0.1', u'localhost', u'-', u'::1'],
    u'machine_name': [u'127.0.0.1', u'localhost', u'-'],
    u'user_name': [u'N/A', u'-'],
}
BLACK_LIST = {}
for prefix in [u'source', u'target']:
  for sufix in BASIC_BLACK_LIST.keys():
    BLACK_LIST[prefix + u':' + sufix] = BASIC_BLACK_LIST[sufix]

# Set of handy helper functions.
def GetNodeTypeFromInformation(information):
  """Return type of information.

  Args:
      information (string): canonical name of interesting field.
  Returns:
    str: part of information string after ":".
  """
  return information.split(u':')[1]


def FirstTrue(values, default=None):
  """Return first True (not None, not empty...) value or default.

  Args:
    values (iterable): list of values to choose from.
    default (optional): default return.
  Returns:
    ?: first True object.
  Used to determine a meaningful name for a machine.
  """
  for value in values:
    if value:
      return value
  return default


def GetPlasoFilename(event):
  """Returns path to plaso file that the log came from.

  Actual directories in actual path are in reversed order.
  Example: /tmp/work/dump.plaso ---> dump.plaso/work/tmp/
  The path is more readable in visualization (because of trimming long names).

  Args:
    event (dict): json serialized plaso event.
  Returns:
    str: path to plaso file in reversed order (look down at the example).
  """
  spec = event.get(u'pathspec', {})
  if isinstance(spec, basestring):
    # This is needed if data some from elasticsearch. Because it likes to cast
    # things to strings.
    spec = eval(spec)  # pylint: disable=eval-used

  while u'parent' in spec:
    spec = spec[u'parent']
  location = spec.get(u'location', u'')
  t_location = u'/'.join(location.split(u'/')[::-1])
  return t_location


class ParserManager(object):
  """Manages individual parsers.

  You can add a parser with RegisterParser() or parse event with Parse().
  """

  # Keys are event data_types and values are parser classes.
  _parser_clases = {}
  _parsed_events = 0

  @classmethod
  def GetNextEventId(cls):
    """Provides a way to generate unique identifiers for events.

    This is used in case the data does not come from elasticsearch.
    """
    cls._parsed_events += 1
    return cls._parsed_events

  @classmethod
  def GetParsedTypes(cls):
    """Return data_types that can be parsed.

    Used for generating an elasticsearch query in timesketch.
    """
    return cls._parser_clases.keys()

  @classmethod
  def RegisterParser(cls, parser_cls):
    """Adds parser to a specific data_type.

    Currently each data_type can have at most one parser.
    """
    cls._parser_clases[parser_cls.DATA_TYPE] = parser_cls

  @classmethod
  def Parse(cls, event):
    """Determines which parser should be used and uses it.

    Parser is chosen based on data_type of event.
    After the parsing, some enhancements are done to data.
    Users (names and ids) are extended by first reasonable machine
    identifier. Timestamps and event_id are added. Information is checked
    against the BLACKLIST.

    Args:
        event: Loaded plaso json (dict).
    Returns:
        dict: information names and values.
    """
    raw_data_type = event.get(u'data_type')
    data_type = None

    if isinstance(raw_data_type, basestring):
      data_type = raw_data_type
    elif isinstance(raw_data_type, dict):
      data_type = raw_data_type.get(u'stream')

    if data_type in cls._parser_clases:
      parsed = cls._parser_clases[data_type].Parse(event)
      for key in parsed.keys():
        if parsed[key] in BLACK_LIST.get(key, []):
          del parsed[key]

      if not parsed:
        return {}

      parsed[u'data_type'] = event[u'data_type']
      target_id = FirstTrue([
          parsed.get(TARGET_MACHINE_NAME), parsed.get(TARGET_MACHINE_IP),
          parsed.get(TARGET_PLASO), u'UNKNOWN'
      ])

      for key in [TARGET_USER_NAME, TARGET_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + u'@' + target_id

      source_id = FirstTrue([
          parsed.get(SOURCE_MACHINE_NAME), parsed.get(SOURCE_MACHINE_IP),
          parsed.get(SOURCE_PLASO), u'UNKNOWN'
      ])

      for key in [SOURCE_USER_NAME, SOURCE_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + u'@' + source_id

      parsed[TIMESTAMP] = event.get(TIMESTAMP)
      parsed[EVENT_ID] = event.get(u'timesketch_id', cls.GetNextEventId())

      return parsed

  @classmethod
  def ParseLine(cls, line):
    """Front-end for ParseEvent() that parses one line.

    Args:
        line (str): event in json_line format.

    Returns:
        dict: information names and values.
    """
    event = json.loads(line)
    return cls.ParseEvent(event)

  @classmethod
  def ParseEvent(cls, event):
    """Front-end for Parse() that does not care about exceptions.

    Args:
      event (dict): event in json_line format.

    Returns:
      dict: information names and values. Empty if event does not contain
      valuable (parseable) information. None if error occurred.
    """
    data = None
    try:
      data = cls.Parse(event)
    except KeyboardInterrupt:
      raise
    except Exception as e: # pylint: disable=broad-except
      print(e, file=sys.stderr)
      print(event, file=sys.stderr)
      traceback.print_exc(file=sys.stdout)
    return data


# Classes for ssh and other forms of 'machine jumping' parsers.
# For examples of give types, see tests/parsers.py.

class LinuxUtmpEventParser(object):
  """Parser for linux:utm:event data_type."""
  DATA_TYPE = u'linux:utmp:event'

  @classmethod
  def Parse(cls, event):
    """Parsing information directly from event fields."""
    data = {}
    data[TARGET_PLASO] = GetPlasoFilename(event)
    data[TARGET_MACHINE_NAME] = event.get(u'hostname')
    # NOTE: I do not care about PID nor terminal id.

    ip_address = event.get(u'ip_address', {})
    if isinstance(ip_address, dict):
      data[SOURCE_MACHINE_IP] = ip_address.get(u'stream')
    elif isinstance(ip_address, basestring):
      data[SOURCE_MACHINE_IP] = ip_address

    data[SOURCE_MACHINE_NAME] = event.get(u'computer_name')
    data[TARGET_USER_NAME] = event.get(u'user')
    return data

ParserManager.RegisterParser(LinuxUtmpEventParser)


class WinEvtxEventParser(object):
  """Parser for windows:evtx:record data_type. For example see tests.py."""
  DATA_TYPE = u'windows:evtx:record'

  @classmethod
  def Parse(cls, event):
    """Parsing information based on position in event.strings. """

    data = {}
    event_id = event.get(u'event_identifier')
    strings = event.get(u'strings')
    if not strings:
      return {}

    if not isinstance(strings, list):
      strings = eval(strings)  # pylint: disable=eval-used

    if event_id == 4624:  # An account was successfully logged on.
      data[SOURCE_PLASO] = GetPlasoFilename(event)
      data[SOURCE_MACHINE_NAME] = event[u'computer_name']
      field_mapper = {
          SOURCE_USER_ID: 0,
          SOURCE_USER_NAME: 1,
          TARGET_USER_ID: 4,
          TARGET_USER_NAME: 5,
          TARGET_MACHINE_NAME: 11,
          TARGET_MACHINE_IP: 18,
      }
      for field_name, field_index in field_mapper.items():
        data[field_name] = strings[field_index]
      return data

    elif event_id == 4648:  # Login with certificate.
      field_mapper = {
          SOURCE_USER_ID: 0,
          SOURCE_USER_NAME: 1,
          TARGET_USER_NAME: 5,
          TARGET_MACHINE_NAME: 8,
          TARGET_MACHINE_IP: 12,
      }

      for field_name, field_index in field_mapper.items():
        data[field_name] = strings[field_index]
      data[SOURCE_MACHINE_NAME] = event[u'computer_name']
      return data

    else:
      return {}

ParserManager.RegisterParser(WinEvtxEventParser)


class BsmEventParser(object):
  """Parser for bsm:event data_type. For example see tests.py."""

  DATA_TYPE = u'bsm:event'
  SUCCESS_REGEXP = re.compile(r'.*BSM_TOKEN_RETURN32: Success*.')
  USER_REGEXP = re.compile(r'BSM_TOKEN_TEXT: successful login (\S+)\]')
  TOKEN_REGEXP = re.compile(r'\[BSM_TOKEN_SUBJECT32_EX: (.*?)\]')
  # NOTE: Could parse logout (local (6153)) as well.

  @classmethod
  def Parse(cls, event):
    """Parsing event.message with regexps."""

    data = {}
    data[TARGET_PLASO] = GetPlasoFilename(event)
    event_type = event.get(u'event_type')
    message = event.get(u'message', '')
    if not (event_type == u'OpenSSH login (32800)' and
            cls.SUCCESS_REGEXP.match(message)):
      return {}

    user = cls.USER_REGEXP.search(message)
    if user:
      data[TARGET_USER_NAME] = user.group(1)

    raw_tokens = cls.TOKEN_REGEXP.search(message)
    token_dict = {}
    if raw_tokens:
      tokens = raw_tokens.group(1).split(u',')
      for token in tokens:
        key, value = token.strip(u' )').split(u'(')
        token_dict[key] = value
    data[SOURCE_MACHINE_IP] = token_dict.get(u'terminal_ip')
    data[TARGET_USER_ID] = token_dict.get(u'uid')

    # NOTE: other potentially interesting things:
    # aid, euid, egid, uid, gid, pid, session_id, terminal_port, terminal_ip

    return data

ParserManager.RegisterParser(BsmEventParser)


class SysLogParser(object):
  """Parser for syslog:line data_type. For example see tests.py.

  Plaso will be parsing these. Will be changed in the future.
  """

  DATA_TYPE = u'syslog:line'
  MATCH_REGEXP = re.compile(
      r'.*Accepted password for (?P<user>\S+) '
      r'from (?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}) port (?P<port>(\d+)).*')

  # NOTE: I do not care for fail attempts tight now.

  @classmethod
  def Parse(cls, event):
    """Parsing event.message with regexp. """
    match = cls.MATCH_REGEXP.match(event.get(u'message', ''))
    if not match:
      return {}

    data = {}
    data[TARGET_PLASO] = GetPlasoFilename(event)
    data[TARGET_USER_NAME] = match.group(u'user')
    data[SOURCE_MACHINE_IP] = match.group(u'ip')
    # NOTE: I do not care for port right now.
    return data

ParserManager.RegisterParser(SysLogParser)


class SysLogSshParser(object):
  """Parser for syslog:ssh:login data_type. For example see tests.py.
  """
  DATA_TYPE = u'syslog:ssh:login'
  MATCH_REGEXP = re.compile(
      r'.*Successful login of user: (?P<user>\S+)\s?from '
      r'(?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}):(?P<port>(\d+)).*')
  # Care fore tricky \s whitespaces.

  @classmethod
  def Parse(cls, event):
    """Parse event message with regexp."""
    data = {}
    data[TARGET_PLASO] = GetPlasoFilename(event)
    match = cls.MATCH_REGEXP.match(event.get(u'message', u''))
    if not match:
      return {}

    data[TARGET_MACHINE_NAME] = event.get(u'hostname', u'-')
    data[TARGET_USER_NAME] = match.group(u'user')
    data[SOURCE_MACHINE_IP] = match.group(u'ip')
    # NOTE I do not care for authentication method nor pid.
    return data

ParserManager.RegisterParser(SysLogSshParser)
