# -*- coding: utf-8 -*-
"""Parser for linux:utm:event data_type."""

from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class LinuxUtmpEventParser(parser_interface.ParserInterface):
  """Parser for linux:utmp:event data_type."""
  DATA_TYPE = u'linux:utmp:event'

  @classmethod
  def Parse(cls, event):
    """Parsing information directly from event fields.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      dict[str, str]: information parsed from event.
    """
    data = {}
    data[utils.TARGET_PLASO] = utils.GetImageName(event)
    data[utils.TARGET_MACHINE_NAME] = event.get(u'hostname')
    # NOTE: I do not care about PID nor terminal id.

    ip_address = event.get(u'ip_address', {})
    if isinstance(ip_address, dict):
      data[utils.SOURCE_MACHINE_IP] = ip_address.get(u'stream')
    elif isinstance(ip_address, basestring):
      data[utils.SOURCE_MACHINE_IP] = ip_address

    data[utils.SOURCE_MACHINE_NAME] = event.get(u'computer_name')
    data[utils.TARGET_USER_NAME] = event.get(u'user')
    return data

manager.ParserManager.RegisterParser(LinuxUtmpEventParser)
