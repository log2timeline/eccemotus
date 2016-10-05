# -*- coding: utf-8 -*-
"""Parser for bsm:event data_type."""

import re

from eccemotus.lib import event_data
from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class BsmEventParser(parser_interface.ParserInterface):
  """Parser for bsm:event data_type."""

  DATA_TYPE = u'bsm:event'
  SUCCESS_REGEXP = re.compile(r'.*BSM_TOKEN_RETURN32: Success*.')
  USER_REGEXP = re.compile(r'BSM_TOKEN_TEXT: successful login (\S+)\]')
  TOKEN_REGEXP = re.compile(r'\[BSM_TOKEN_SUBJECT32_EX: (.*?)\]')

  @classmethod
  def Parse(cls, event):
    """Parsing event.message with regexps.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """

    data = event_data.EventData()
    data.Add(event_data.Plaso(target=True, value=utils.GetImageName(event)))
    event_type = event.get(u'event_type')
    message = event.get(u'message', '')
    if not (event_type == u'OpenSSH login (32800)' and
            cls.SUCCESS_REGEXP.match(message)):
      return event_data.EventData()

    user = cls.USER_REGEXP.search(message)
    if user:
      data.Add(event_data.UserName(target=True, value=user.group(1)))

    raw_tokens = cls.TOKEN_REGEXP.search(message)
    token_dict = {}
    if raw_tokens:
      tokens = raw_tokens.group(1).split(u',')
      for token in tokens:
        key, value = token.strip(u' )').split(u'(')
        token_dict[key] = value

    machine_ip = token_dict.get(u'terminal_ip')
    data.Add(event_data.Ip(source=True, value=machine_ip))
    data.Add(event_data.UserId(target=True, value=token_dict.get(u'uid')))

    return data

manager.ParserManager.RegisterParser(BsmEventParser)
