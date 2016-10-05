# -*- coding: utf-8 -*-
"""Parser for syslog:ssh:login data_type."""

import re

from eccemotus.lib import event_data
from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class SysLogSshParser(parser_interface.ParserInterface):
  """Parser for syslog:ssh:login data_type."""
  DATA_TYPE = u'syslog:ssh:login'
  # Care for tricky \s whitespaces.
  MATCH_REGEXP = re.compile(
      r'.*Successful login of user: (?P<user>\S+)\s?from '
      r'(?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3}):(?P<port>(\d+)).*')

  @classmethod
  def Parse(cls, event):
    """Parse event message with regexp.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    data = event_data.EventData()
    match = cls.MATCH_REGEXP.match(event.get(u'message', u''))
    if not match:
      return event_data.EventData()

    data.Add(event_data.Plaso(target=True, value=utils.GetImageName(event)))
    data.Add(event_data.MachineName(
        target=True, value=event.get(u'hostname', u'-')))
    data.Add(event_data.UserName(target=True, value=match.group(u'user')))
    data.Add(event_data.Ip(source=True, value=match.group(u'ip')))
    # NOTE I do not care for authentication method nor pid.
    return data

manager.ParserManager.RegisterParser(SysLogSshParser)
