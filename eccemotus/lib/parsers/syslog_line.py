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
    """Parses event.message with regexp.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    match = cls.MATCH_REGEXP.match(event.get(u'message', ''))
    if not match:
      return event_data.EventData()

    data = event_data.EventData()

    storage_file_name = utils.GetImageName(event)
    storage_datum = event_data.StorageFileName(
        target=True, value=storage_file_name)
    data.Add(storage_datum)

    target_user_name = match.group(u'user')
    target_user_name_datum = event_data.UserName(
        target=True, value=target_user_name)
    data.Add(target_user_name_datum)
    source_ip = match.group(u'ip')
    source_ip_datum = event_data.Ip(source=True, value=source_ip)
    data.Add(source_ip_datum)

    return data

manager.ParserManager.RegisterParser(SysLogParser)
