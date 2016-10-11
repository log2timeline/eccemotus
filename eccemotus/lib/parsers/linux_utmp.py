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
    """Parses event data directly from event fields.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """
    data = event_data.EventData()
    storage_file_name = utils.GetImageName(event)
    storage_datum = event_data.StorageFileName(
        target=True, value=storage_file_name)
    data.Add(storage_datum)
    target_machine_name = event.get(u'hostname')
    target_machine_name_datum = event_data.MachineName(
        target=True, value=target_machine_name)
    data.Add(target_machine_name_datum)

    source_ip_field = event.get(u'ip_address', {})
    if isinstance(source_ip_field, dict):
      source_ip = source_ip_field.get(u'stream')
      source_ip_datum = event_data.Ip(source=True, value=source_ip)
      data.Add(source_ip_datum)
    elif isinstance(source_ip_field, basestring):
      source_ip_datum = event_data.Ip(source=True, value=source_ip_field)
      data.Add(source_ip_datum)

    source_machine_name = event.get(u'computer_name')
    source_machine_name_datum = event_data.MachineName(
        source=True, value=source_machine_name)
    data.Add(source_machine_name_datum)
    target_user_name = event.get(u'user')
    target_user_name_datum = event_data.UserName(
        target=True, value=target_user_name)
    data.Add(target_user_name_datum)
    return data

manager.ParserManager.RegisterParser(LinuxUtmpEventParser)
