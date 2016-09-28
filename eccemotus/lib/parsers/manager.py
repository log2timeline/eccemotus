# -*- coding: utf-8 -*-
"""Parsers management.

Provides way for parsing remote access related information from plaso logs.
Use ParserManager.Parse(event) and it will extract interesting fields in context
of lateral movement from plaso event.

It is parser's responsibility to register to manager via RegisterParser method.
"""

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
    """Return data_types that can be parsed.

    Used for generating an elasticsearch query in timesketch.
    """
    return cls._parser_clases.keys()

  @classmethod
  def RegisterParser(cls, parser_cls):
    """Adds parser to a specific data_type.

    Currently each data_type can have at most one parser.

    Args:
      parser_cls (ParserInterface): class to register as a new parser.

    """
    cls._parser_clases[parser_cls.DATA_TYPE] = parser_cls

  @classmethod
  def Parse(cls, event):
    """Determines which parser should be used and uses it.

    Parser is chosen based on data_type of event.
    After the parsing, some enhancements are done to data.
    Users (names and ids) are extended by first reasonable machine
    identifier. Timestamps and event_id are added. Information is checked
    against the BLACKLIST.

    Args:
        event: Loaded plaso json (dict).
    Returns:
        dict: information names and values.
    """
    raw_data_type = event.get(u'data_type')
    data_type = None

    if isinstance(raw_data_type, basestring):
      data_type = raw_data_type
    elif isinstance(raw_data_type, dict):
      data_type = raw_data_type.get(u'stream')

    if data_type in cls._parser_clases:
      parsed = cls._parser_clases[data_type].Parse(event)
      for key in parsed.keys():
        if parsed[key] in utils.BLACK_LIST.get(key, []):
          del parsed[key]

      if not parsed:
        return {}

      parsed[u'data_type'] = event[u'data_type']
      target_id = utils.FirstTrue([
          parsed.get(utils.TARGET_MACHINE_NAME),
          parsed.get(utils.TARGET_MACHINE_IP),
          parsed.get(utils.TARGET_PLASO), u'UNKNOWN'
      ])

      for key in [utils.TARGET_USER_NAME, utils.TARGET_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + u'@' + target_id

      source_id = utils.FirstTrue([
          parsed.get(utils.SOURCE_MACHINE_NAME),
          parsed.get(utils.SOURCE_MACHINE_IP),
          parsed.get(utils.SOURCE_PLASO), u'UNKNOWN'
      ])

      for key in [utils.SOURCE_USER_NAME, utils.SOURCE_USER_ID]:
        if key in parsed:
          parsed[key] = parsed[key] + u'@' + source_id

      parsed[utils.TIMESTAMP] = event.get(utils.TIMESTAMP)
      parsed[utils.EVENT_ID] = event.get(u'timesketch_id', cls.GetNextEventId())
      return parsed
    else:
      return {}
