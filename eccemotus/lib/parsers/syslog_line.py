# -*- coding: utf-8 -*-
"""Parser for syslog:line data_type."""

import re

from eccemotus.lib import event_data
from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class SysLogParser(parser_interface.ParserInterface):
  """Parser for syslog:line data_type."""
  DATA_TYPE = u'syslog:line'
  MATCH_REGEXP = re.compile(
      r'.*Accepted password for (?P<user>\S+) '
      r'from (?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}) port (?P<port>(\d+)).*')

  @classmethod
  def Parse(cls, event):
    """Parsing event.message with regexp.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    match = cls.MATCH_REGEXP.match(event.get(u'message', ''))
    if not match:
      return event_data.EventData()

    data = event_data.EventData()
    data.Add(event_data.Plaso(target=True, value=utils.GetImageName(event)))
    data.Add(event_data.UserName(target=True, value=match.group(u'user')))
    data.Add(event_data.Ip(source=True, value=match.group(u'ip')))

    return data

manager.ParserManager.RegisterParser(SysLogParser)
