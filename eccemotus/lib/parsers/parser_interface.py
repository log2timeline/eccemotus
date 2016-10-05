# -*- coding: utf-8 -*-
"""Contains event parser interface class.

All parsers should implement Parse method, that extracts valuable data from
plaso event in context of lateral movement.
Every parser should have DATA_TYPE property which specifies events of which
data_types will be parsed by this parser.
"""

import abc

# Since abc does not seem to have an @abc.abstractclassmethod we're using
# @abc.abstractmethod instead and shutting up pylint about:
# E0213: Method should have "self" as first argument.
# pylint: disable=no-self-argument

class ParserInterface(object):
  """Interface that every parser should implement.

  This does not add new functionality, but it makes the code more readable.
  """

  @abc.abstractproperty
  def DATA_TYPE(cls):
    """Specifies which plaso events are parsed by this parser.

    This is meant as an abstractclassproperty.

    Returns:
      str: plaso event identifier.
    """
    pass


  @abc.abstractmethod
  def Parse(cls, event):
    """Parse plaso event.

    This is meant as an abstractclassmethod.

    Args:
      event (dict): dict serialized plaso event.

    Returns:
        event_data.EventData: event data extracted from event.
    """
    pass
