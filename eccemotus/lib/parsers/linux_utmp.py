# -*- coding: utf-8 -*-
"""Parser for linux:utm:event data_type."""

from eccemotus.lib import event_data
from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class LinuxUtmpEventParser(parser_interface.ParserInterface):
  """Parser for linux:utmp:event data_type."""
  DATA_TYPE = u'linux:utmp:event'

  @classmethod
  def Parse(cls, event):
    """Parsing event data directly from event fields.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    data = event_data.EventData()
    data.Add(event_data.Plaso(target=True, value=utils.GetImageName(event)))
    data.Add(event_data.MachineName(target=True, value=event.get(u'hostname')))

    ip_address = event.get(u'ip_address', {})
    if isinstance(ip_address, dict):
      data.Add(event_data.Ip(source=True, value=ip_address.get(u'stream')))
    elif isinstance(ip_address, basestring):
      data.Add(event_data.Ip(source=True, value=ip_address))

    data.Add(event_data.MachineName(
        source=True, value=event.get(u'computer_name')))
    data.Add(event_data.UserName(target=True, value=event.get(u'user')))
    return data

manager.ParserManager.RegisterParser(LinuxUtmpEventParser)
