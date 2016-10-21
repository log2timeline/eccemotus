# -*- coding: utf-8 -*-
"""Parsers management.

Provides way for parsing remote access related event data from plaso logs.
Use ParserManager.Parse(event) and it will extract interesting fields in context
of lateral movement from plaso event.

It is parser's responsibility to register to manager via RegisterParser method.
"""

from eccemotus.lib import event_data
from eccemotus.lib.parsers import utils

class ParserManager(object):
  """Manages individual parsers.

  You can add a parser with RegisterParser() or parse event with Parse().
  """

  # Keys are event data_types and values are parser classes.
  _parser_clases = {}
  _parsed_events = 0

  @classmethod
  def GetNextEventId(cls):
    """Provides a way to generate unique identifiers for events.

    This is used in case the data does not come from elasticsearch.
    """
    cls._parsed_events += 1
    return cls._parsed_events

  @classmethod
  def GetParsedTypes(cls):
    """Returns data_types that can be parsed.

    Used for generating an elasticsearch query in timesketch.
    """
    return cls._parser_clases.keys()

  @classmethod
  def RegisterParser(cls, parser_cls):
    """Adds parser to a specific data_type.

    Currently each data_type can have at most one parser.

    Args:
      parser_cls (ParserInterface): class to register as a new parser.\
    """
    cls._parser_clases[parser_cls.DATA_TYPE] = parser_cls

  @classmethod
  def Parse(cls, event):
    """Determines which parser should be used and uses it.

    Parser is chosen based on data_type of event.
    After parsing, some enhancements are done to data.
    Users (names and ids) are extended by first reasonable machine identifier.
    Adds timestamps and event_id.

    Args:
        event (dict): dict serialized plaso event.

    Returns:
        event_data.EventData: event data extracted from event.
    """
    raw_data_type = event.get(u'data_type')
    data_type = None

    if isinstance(raw_data_type, basestring):
      data_type = raw_data_type
    elif isinstance(raw_data_type, dict):
      data_type = raw_data_type.get(u'stream')

    if data_type in cls._parser_clases:
      parsed_data = cls._parser_clases[data_type].Parse(event)

      if not parsed_data or parsed_data.IsEmpty():
        return event_data.EventData()

      parsed_data.event_data_type = data_type
      target_datum_candidates = [
          parsed_data.Get(event_data.MachineName(target=True)),
          parsed_data.Get(event_data.Ip(target=True)),
          parsed_data.Get(event_data.StorageFileName(target=True))]
      target_id = utils.FirstValidDatum(
          target_datum_candidates, default=u'UNKNOWN')

      for inf in [event_data.UserName(target=True),
                  event_data.UserId(target=True)]:
        inf = parsed_data.Get(inf)
        if inf:
          inf.value += u'@' + target_id

      source_datum_candidates = [
          parsed_data.Get(event_data.MachineName(source=True)),
          parsed_data.Get(event_data.Ip(source=True)),
          parsed_data.Get(event_data.StorageFileName(source=True))]
      source_id = utils.FirstValidDatum(
          source_datum_candidates, default=u'UNKNOWN')

      for inf in [event_data.UserName(source=True),
                  event_data.UserId(source=True)]:
        inf = parsed_data.Get(inf)
        if inf:
          inf.value += u'@' + source_id


      parsed_data.timestamp = event.get(u'timestamp')
      uuid = event.get(u'uuid', cls.GetNextEventId())
      parsed_data.event_id = event.get(u'timesketch_id', uuid)
      return parsed_data
    else:
      return event_data.EventData()
