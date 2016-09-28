# -*- coding: utf-8 -*-
"""Parser for syslog:line data_type."""

import re

from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class SysLogParser(parser_interface.ParserInterface):
  """Parser for syslog:line data_type."""
  DATA_TYPE = u'syslog:line'
  MATCH_REGEXP = re.compile(
      r'.*Accepted password for (?P<user>\S+) '
      r'from (?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}) port (?P<port>(\d+)).*')

  # NOTE: I do not care for fail attempts tight now.

  @classmethod
  def Parse(cls, event):
    """Parsing event.message with regexp.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      dict[str, str]: information parsed from event.
    """
    match = cls.MATCH_REGEXP.match(event.get(u'message', ''))
    if not match:
      return {}

    data = {}
    data[utils.TARGET_PLASO] = utils.GetImageName(event)
    data[utils.TARGET_USER_NAME] = match.group(u'user')
    data[utils.SOURCE_MACHINE_IP] = match.group(u'ip')
    # NOTE: I do not care for port right now.
    return data

manager.ParserManager.RegisterParser(SysLogParser)
