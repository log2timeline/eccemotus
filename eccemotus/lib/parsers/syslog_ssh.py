# -*- coding: utf-8 -*-
"""Parser for syslog:ssh:login data_type."""

import re

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
      dict[str, str]: information parsed from event.
    """
    data = {}
    data[utils.TARGET_PLASO] = utils.GetImageName(event)
    match = cls.MATCH_REGEXP.match(event.get(u'message', u''))
    if not match:
      return {}

    data[utils.TARGET_MACHINE_NAME] = event.get(u'hostname', u'-')
    data[utils.TARGET_USER_NAME] = match.group(u'user')
    data[utils.SOURCE_MACHINE_IP] = match.group(u'ip')
    # NOTE I do not care for authentication method nor pid.
    return data

manager.ParserManager.RegisterParser(SysLogSshParser)
