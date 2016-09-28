# -*- coding: utf-8 -*-
"""Parser for windows:evtx:record data_type."""

from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class WinEvtxEventParser(parser_interface.ParserInterface):
  """Parser for windows:evtx:record data_type."""
  DATA_TYPE = u'windows:evtx:record'

  @classmethod
  def Parse(cls, event):
    """Parsing information based on position in event.strings.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      dict[str, str]: information parsed from event.
    """

    data = {}
    event_id = event.get(u'event_identifier')
    strings = event.get(u'strings')
    if not strings:
      return {}

    if not isinstance(strings, list):
      strings = eval(strings)  # pylint: disable=eval-used

    if event_id == 4624:  # An account was successfully logged on.
      data[utils.SOURCE_PLASO] = utils.GetImageName(event)
      data[utils.SOURCE_MACHINE_NAME] = event[u'computer_name']
      field_mapper = {
          utils.SOURCE_USER_ID: 0,
          utils.SOURCE_USER_NAME: 1,
          utils.TARGET_USER_ID: 4,
          utils.TARGET_USER_NAME: 5,
          utils.TARGET_MACHINE_NAME: 11,
          utils.TARGET_MACHINE_IP: 18,
      }
      for field_name, field_index in field_mapper.items():
        data[field_name] = strings[field_index]
      return data

    elif event_id == 4648:  # Login with certificate.
      field_mapper = {
          utils.SOURCE_USER_ID: 0,
          utils.SOURCE_USER_NAME: 1,
          utils.TARGET_USER_NAME: 5,
          utils.TARGET_MACHINE_NAME: 8,
          utils.TARGET_MACHINE_IP: 12,
      }

      for field_name, field_index in field_mapper.items():
        data[field_name] = strings[field_index]
      data[utils.SOURCE_MACHINE_NAME] = event[u'computer_name']
      return data

    else:
      return {}

manager.ParserManager.RegisterParser(WinEvtxEventParser)
