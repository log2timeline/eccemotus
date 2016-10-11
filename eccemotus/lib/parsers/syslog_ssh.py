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
    """Parses event message with regexp.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    data = event_data.EventData()
    match = cls.MATCH_REGEXP.match(event.get(u'message', u''))
    if not match:
      return event_data.EventData()

    storage_file_name = utils.GetImageName(event)
    target_storage_datum = event_data.StorageFileName(
        target=True, value=storage_file_name)
    data.Add(target_storage_datum)
    target_machine_name = event.get(u'hostname', u'-')
    target_machine_name_datum = event_data.MachineName(
        target=True, value=target_machine_name)
    data.Add(target_machine_name_datum)
    target_user_name = match.group(u'user')
    target_user_name_datum = event_data.UserName(
        target=True, value=target_user_name)
    data.Add(target_user_name_datum)
    source_ip = match.group(u'ip')
    source_ip_datum = event_data.Ip(source=True, value=source_ip)
    data.Add(source_ip_datum)
    # NOTE I do not care for authentication method nor pid.
    return data

manager.ParserManager.RegisterParser(SysLogSshParser)
