# -*- coding: utf-8 -*-
"""Parser for windows:evtx:record data_type."""

from eccemotus.lib import event_data
from eccemotus.lib.parsers import manager
from eccemotus.lib.parsers import parser_interface
from eccemotus.lib.parsers import utils


class WinEvtxEventParser(parser_interface.ParserInterface):
  """Parser for windows:evtx:record data_type."""
  DATA_TYPE = u'windows:evtx:record'

  @classmethod
  def Parse(cls, event):
    """Parsing event data based on position in event.strings.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
      event_data.EventData: event data parsed from event.
    """

    data = event_data.EventData()
    event_id = event.get(u'event_identifier')
    strings = event.get(u'strings')
    if not strings:
      return event_data.EventData()

    if not isinstance(strings, list):
      strings = eval(strings)  # pylint: disable=eval-used

    if event_id == 4624:  # An account was successfully logged on.
      data.Add(event_data.Plaso(value=utils.GetImageName(event), source=True))
      data.Add(event_data.MachineName(
          source=True, value=event.get(u'computer_name', '')))
      field_mapper = {
          event_data.UserId(source=True): 0,
          event_data.UserName(source=True): 1,
          event_data.UserId(target=True): 4,
          event_data.UserName(target=True): 5,
          event_data.MachineName(target=True): 11,
          event_data.Ip(target=True): 18,
      }
      for datum, field_index in field_mapper.items():
        datum.value = strings[field_index]
        data.Add(datum)

    elif event_id == 4648:  # Login with certificate.
      field_mapper = {
          event_data.UserId(source=True): 0,
          event_data.UserName(source=True): 1,
          event_data.UserName(target=True): 5,
          event_data.MachineName(target=True): 8,
          event_data.Ip(target=True): 12,
      }

      for datum, field_index in field_mapper.items():
        datum.value = strings[field_index]
        data.Add(datum)

      data.Add(event_data.MachineName(
          source=True, value=event[u'computer_name']))

    return data

manager.ParserManager.RegisterParser(WinEvtxEventParser)
