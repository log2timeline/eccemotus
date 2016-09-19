# -*- coding: utf-8 -*-
"""Provides easy way for parsing ssh related information from plaso logs.

Use ParserManager.parse(log) and it will interesting fields in context of
lateral movement.
"""
from __future__ import print_function
import re
import sys
import traceback
import json

# Canonical names for interesting information (fields).
EVENT_ID = 'event_id'
TIMESTAMP = 'timestamp'

SOURCE_MACHINE_IP = 'source:ip'
SOURCE_MACHINE_NAME = 'source:machine_name'
SOURCE_PLASO = 'source:plaso'
SOURCE_USER_ID = 'source:user_id'
SOURCE_USER_NAME = 'source:user_name'

TARGET_MACHINE_IP = 'target:ip'
TARGET_MACHINE_NAME = 'target:machine_name'
TARGET_PLASO = 'target:plaso'
TARGET_USER_ID = 'target:user_id'
TARGET_USER_NAME = 'target:user_name'

# Black lists for common invalid or uninteresting field values.
BASIC_BLACK_LIST = {
    'ip': ['127.0.0.1', 'localhost', '-', '::1'],
    'machine_name': ['127.0.0.1', 'localhost', '-'],
    'user_name': ['N/A', '-'],
}
BLACK_LIST = {}
for prefix in ['source', 'target']:
  for sufix in BASIC_BLACK_LIST.keys():
    BLACK_LIST[prefix + ':' + sufix] = BASIC_BLACK_LIST[sufix]

# TODO add class for mac:asl:event   probably certificates
# TODO inheritance ?
# TODO windows sharing logs

# Set of handy helper functions.
def get_type(information):
  """ Return type of information.

  Args:
      information (string): canonical name of interesting field.
  Returns:
    str: part of information string after ":".
  """
  return information.split(":")[1]


def first_true(values, default=None):
  """ Return first True (not None, not empty...) value or default.

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


def get_plaso_filename(event):
  """ Returns path to plaso file that the log came from.

    Args:
      event (plaso.event (dict)): plaso event.
    Returns:
      str: path to plaso file in reversed order (look down at the example).

    Actual directories in actual path are in reversed order.
    Example: /tmp/work/dump.plaso ---> dump.plaso/work/tmp/
    The path is more readable in visualization (because of trimming long names).
  """
  spec = event.get('pathspec', {})
  if isinstance(spec, basestring):
    # This is needed if data some from elasticsearch. Because it likes to cast
    # things to strings.
    spec = eval(spec) # pylint: disable=eval-used

  while 'parent' in spec:
    spec = spec['parent']
  location = spec.get('location', '')
  t_location = '/'.join(location.split('/')[::-1])
  return t_location


class ParserManager(object):
  """ Manages individual parsers.

  You can add a parser with register_parser() or parse event with parse().
  """

  # Keys are event data_types and values are parser classes.
  _parser_clases = {}
  _parsed_events = 0

  @classmethod
  def get_next_event_id(cls):
    """Provides a way to generate unique identifiers for events.

    This is used in case the data does not come from elasticsearch.
    """
    cls._parsed_events += 1
    return cls._parsed_events

  @classmethod
  def get_parsed_types(cls):
    """Return data_types that can be parsed.

    Used for generating an elasticsearch query in timesketch.
    """
    return cls._parser_clases.keys()

  @classmethod
  def register_parser(cls, parser_cls):
    """Adds parser to a specific data_type.

    Currently each data_type can have at most one parser.
    """
    cls._parser_clases[parser_cls.DATA_TYPE] = parser_cls

  @classmethod
  def parse(cls, event):
    """ Determines which parser should be used and uses it.

    Args:
        event: Loaded plaso json (dict).
    Returns:
        dict: information names and values.

    Parser is chosen based on data_type of event.
    After the parsing, some enhancements are done to data.
    Users (names and ids) are extended by first reasonable machine
    identifier. Timestamps and event_id are added. Information is checked
    against the BLACKLIST.
    """
    raw_data_type = event.get('data_type')
    data_type = None

    if isinstance(raw_data_type, basestring):
      data_type = raw_data_type
    elif isinstance(raw_data_type, dict):
      data_type = raw_data_type.get('stream')
    else:
      print(event, file=sys.stderr)
      print(
          'what is this? This should not happen.',
          raw_data_type,
          file=sys.stderr)
      return {}

    if data_type in cls._parser_clases:
      parsed = cls._parser_clases[data_type].parse(event)
      for key in parsed.keys():
        if parsed[key] in BLACK_LIST.get(key, []):
          del parsed[key]

      if not parsed:
        return {}

      parsed['data_type'] = event['data_type']
      target_id = first_true([
          parsed.get(TARGET_MACHINE_NAME), parsed.get(TARGET_MACHINE_IP),
          parsed.get(TARGET_PLASO), "UNKNOWN"
      ])

      for key in [TARGET_USER_NAME, TARGET_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + '@' + target_id

      source_id = first_true([
          parsed.get(SOURCE_MACHINE_NAME), parsed.get(SOURCE_MACHINE_IP),
          parsed.get(SOURCE_PLASO), "UNKNOWN"
      ])

      for key in [SOURCE_USER_NAME, SOURCE_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + '@' + source_id

      parsed[TIMESTAMP] = event.get(TIMESTAMP)
      parsed[EVENT_ID] = event.get('timesketch_id', cls.get_next_event_id())

      return parsed

  @classmethod
  def parse_line(cls, line):
    """ Front-end for parse_event() that parses one line.

    Args:
        line (str): event in json_line format.

    Returns:
        dict: information names and values.

    """
    event = json.loads(line)
    return cls.parse_event(event)

  @classmethod
  def parse_event(cls, event):
    """ Front-end for parse() that does not care about exceptions.

    Args:
      event (dict): event in json_line format.

    Returns:
      dict: information names and values. Empty if event does not contain
      valuable (parseable) information. None if error occurred.
    """
    data = None
    try:
      data = cls.parse(event)
    except KeyboardInterrupt:
      raise
    except Exception as e: # pylint: disable=broad-except
      print(e, file=sys.stderr)
      print(event, file=sys.stderr)
      traceback.print_exc(file=sys.stdout)
    return data


# Classes for ssh and other forms of 'machine jumping' parsers.
# For examples of give types, see tests/parsers.py

class LinuxUtmpEventParser(object):
  """Parser for linux:utm:event data_type."""
  DATA_TYPE = 'linux:utmp:event'

  @classmethod
  def parse(cls, event):
    """Extracting only important fields."""
    data = {}
    data[TARGET_PLASO] = get_plaso_filename(event)
    data[TARGET_MACHINE_NAME] = event.get('hostname')
    # NOTE: I do not care about PID nor terminal id.

    ip_address = event.get('ip_address', {})
    if isinstance(ip_address, dict):
      data[SOURCE_MACHINE_IP] = ip_address.get('stream')
    elif isinstance(ip_address, basestring):
      data[SOURCE_MACHINE_IP] = ip_address

    data[SOURCE_MACHINE_NAME] = event.get('computer_name')
    data[TARGET_USER_NAME] = event.get('user')
    return data

ParserManager.register_parser(LinuxUtmpEventParser)


class WinEvtxEventParser(object):
  """Parser for windows:evtx:record data_type. For example see tests.py."""
  DATA_TYPE = 'windows:evtx:record'

  @classmethod
  def parse(cls, event):
    """Parsing information based on position in event.strings . """

    # wha is 4675? sids were filtered?!
    # what is 1149
    # 4634 is logout - not interesting, but could be
    # 4769 kerberos ticket: machine-userid-username
    data = {}
    event_id = event.get('event_identifier')
    strings = event.get('strings')
    if not strings:
      return {}

    if not isinstance(strings, list):
      strings = eval(strings) # pylint: disable=eval-used

    if event_id == 4624:  # An account was successfully logged on
      data[SOURCE_PLASO] = get_plaso_filename(event)
      data[SOURCE_MACHINE_NAME] = event['computer_name']
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

    elif event_id == 4648:  # login with certificate
      field_mapper = {
          SOURCE_USER_ID: 0,
          SOURCE_USER_NAME: 1,
          TARGET_USER_NAME: 5,
          TARGET_MACHINE_NAME: 8,
          TARGET_MACHINE_IP: 12,
      }

      for field_name, field_index in field_mapper.items():
        data[field_name] = strings[field_index]
      data[SOURCE_MACHINE_NAME] = event['computer_name']
      return data

    else:
      return {}

ParserManager.register_parser(WinEvtxEventParser)


class BsmEventParser(object):
  """Parser for bsm:event data_type. For example see tests.py."""

  DATA_TYPE = 'bsm:event'
  SUCCESS_REGEXP = re.compile(r'.*BSM_TOKEN_RETURN32: Success*.')
  USER_REGEXP = re.compile(r'BSM_TOKEN_TEXT: successful login (\S+)\]')
  TOKEN_REGEXP = re.compile(r'\[BSM_TOKEN_SUBJECT32_EX: (.*?)\]')
  # NOTE: Could parse logout (local (6153)) as well.

  @classmethod
  def parse(cls, event):
    """Parsing event.message with regexps."""

    data = {}
    data[TARGET_PLASO] = get_plaso_filename(event)
    event_type = event.get('event_type')
    message = event.get('message', '')
    if not (event_type == 'OpenSSH login (32800)' and
            cls.SUCCESS_REGEXP.match(message)):
      return {}

    user = cls.USER_REGEXP.search(message)
    if user:
      data[TARGET_USER_NAME] = user.group(1)

    raw_tokens = cls.TOKEN_REGEXP.search(message)
    token_dict = {}
    if raw_tokens:
      tokens = raw_tokens.group(1).split(',')
      for token in tokens:
        key, value = token.strip(' )').split('(')
        token_dict[key] = value
    data[SOURCE_MACHINE_IP] = token_dict.get('terminal_ip')
    data[TARGET_USER_ID] = token_dict.get('uid')

    # NOTE: other potentially interesting things:
    # aid, euid, egid, uid, gid, pid, session_id, terminal_port, terminal_ip

    return data

ParserManager.register_parser(BsmEventParser)


class SysLogParser(object):
  """Parser for syslog:line data_type. For example see tests.py.

    Plaso will be parsing these. Will be changed in the future.
    TODO check the hostname field.
    """

  DATA_TYPE = 'syslog:line'
  MATCH_REGEXP = re.compile(
      r'.*Accepted password for (?P<user>\S+) '
      r'from (?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}) port (?P<port>(\d+)).*')

  # NOTE: I do not care for fail attempts tight now.

  @classmethod
  def parse(cls, event):
    """Parsing event.message with regexp. """
    match = cls.MATCH_REGEXP.match(event.get('message', ''))
    if not match:
      return {}

    data = {}
    data[TARGET_PLASO] = get_plaso_filename(event)
    data[TARGET_USER_NAME] = match.group('user')
    data[SOURCE_MACHINE_IP] = match.group('ip')
    # NOTE: I do not care for port right now.
    return data

ParserManager.register_parser(SysLogParser)


class SysLogSshParser(object):
  """Parser for syslog:ssh:login data_type. For example see tests.py.

    Plaso is parsing this TODO redo. """
  DATA_TYPE = 'syslog:ssh:login'
  MATCH_REGEXP = re.compile(
      r'.*Successful login of user: (?P<user>\S+)\s?from '
      r'(?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}):(?P<port>(\d+)).*')
  # Care fore tricky \s whitespaces.

  @classmethod
  def parse(cls, event):
    """Parse event message with regexp. """
    data = {}
    data[TARGET_PLASO] = get_plaso_filename(event)
    match = cls.MATCH_REGEXP.match(event.get('message', ''))
    if not match:
      return {}

    data[TARGET_MACHINE_NAME] = event.get('hostname', '-')
    data[TARGET_USER_NAME] = match.group('user')
    data[SOURCE_MACHINE_IP] = match.group('ip')
    # NOTE I do not care for authentication method nor pid.
    return data

ParserManager.register_parser(SysLogSshParser)
