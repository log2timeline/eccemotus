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
    """Parses event.message with regexps.

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
    event_type = event.get(u'event_type')
    message = event.get(u'message', '')
    if not (event_type == u'OpenSSH login (32800)' and
            cls.SUCCESS_REGEXP.match(message)):
      return event_data.EventData()

    user = cls.USER_REGEXP.search(message)
    if user:
      user_name = user.group(1)
      user_name_datum = event_data.UserName(target=True, value=user_name)
      data.Add(user_name_datum)

    raw_tokens = cls.TOKEN_REGEXP.search(message)
    token_dict = {}
    if raw_tokens:
      tokens = raw_tokens.group(1).split(u',')
      for token in tokens:
        key, value = token.strip(u' )').split(u'(')
        token_dict[key] = value

    machine_ip = token_dict.get(u'terminal_ip')
    ip_datum = event_data.Ip(source=True, value=machine_ip)
    data.Add(ip_datum)
    user_id = token_dict.get(u'uid')
    user_id_datum = event_data.UserId(target=True, value=user_id)
    data.Add(user_id_datum)

    return data

manager.ParserManager.RegisterParser(BsmEventParser)
