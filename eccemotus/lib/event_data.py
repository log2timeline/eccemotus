# -*- coding: utf-8 -*-
"""Contains classes to handle data parsed from events."""

import abc

# Since abc does not seem to have an @abc.abstractclassmethod we're using
# @abc.abstractmethod instead and shutting up pylint about:
# E0213: Method should have "self" as first argument.
# pylint: disable=no-self-argument

class EventDatum(object):
  """Interface for event data of various types/names.

  Datum has a value, a flag whether it describes source or a target of given
  event and a name. Name of the datums is based on it's class name and it's
  string representations is returned by GetName method. Full name of the datum
  describes the exact information the datum stores. It is the datum's name
  expanded by whether it is a source or a target.
  """

  def __init__(self, value=None, source=None, target=None):
    """Initialize EventDatum.

    Args:
      value (str): value of the datum.
      source (bool): whether the datum describes event source. source and target
        can not be both True at the same time.
      target (bool): whether the datum describes event target. source and target
        can not be both True at the same time.

    Raises:
      ValueError: if source and target are both True.
    """
    self.value = value
    if target and source:
      raise ValueError(u'Datum can not describe target and source at the same '
                       u'time.')

    self.source = bool(source)
    self.target = bool(target)

  def GetFullName(self):
    """Representation of full datum's name.
    Return: containing:
      bool: whether the datum describes source.
      bool: whether the datum describes target.
      str: datum's name.
    """
    return (self.source, self.target, self.GetName())

  def __repr__(self):
    """Readable printable string representation of datum.

    Mostly used for debugging purposes.

    Return:
      str: string representation of datum.
    """
    return (self.source, self.target, self.GetName(), self.value).__repr__()

  @abc.abstractmethod
  def GetName(cls):
    """Datum's name.

    Return:
      str: datum's name.
    """
    pass

class Ip(EventDatum):
  """Class to hold data about ip address."""
  @classmethod
  def GetName(cls):
    """Name for Ip.

    Return:
      str: u'ip'.
    """
    return u'ip'

class MachineName(EventDatum):
  """Class to hold data about machine name."""
  @classmethod
  def GetName(cls):
    """Name for MachineName.

    Returns:
      str: u'machine_name'.
    """
    return u'machine_name'

class Plaso(EventDatum):
  """Class to hold data about plaso file name."""
  @classmethod
  def GetName(cls):
    """Name for plaso.

    Returns:
      str: u'plaso'.
    """
    return u'plaso'

class UserId(EventDatum):
  """Class to hold data about user id."""
  @classmethod
  def GetName(cls):
    """Name for UserId.

    Returns:
      str: u'user_id'.
    """
    return u'user_id'

class UserName(EventDatum):
  """Class to hold data about user name."""
  @classmethod
  def GetName(cls):
    """Name for UserName.

    Returns:
      str: u'user_name'.
    """
    return u'user_name'

class EventData(object):
  """Collection of EventDatum used to manage data extracted from events.

  Data are indexed by their FullName so for each FullName there can be only one
  datum.
  """

  # Black lists for common invalid or uninteresting datum types and values.
  BLACK_LIST = {
      Ip: set([u'127.0.0.1', u'localhost', u'-', u'::1']),
      MachineName: set([u'127.0.0.1', u'localhost', u'-']),
      UserName: set([u'N/A', u'-']),
  }

  def __init__(
      self, data=None, event_data_type=None, event_id=None, timestamp=None):
    """Initialize empty EventData.

    Args:
      data (iterable[EventDatum]): initial data for this collection.
      event_data_type (str): plaso event data_type.
      event_id (int|str): event identifier.
      timestamp (int): timestamp of event.
    """
    if data is None:
      data = []
    self._index = {}
    self.event_id = event_id
    self.timestamp = timestamp
    self.event_data_type = event_data_type
    for datum in data:
      self.Add(datum)

  def Add(self, datum):
    """Adds datum to EventData.

    Args:
      datum (EventDatum): event datum.
    """
    black_list = self.BLACK_LIST.get(datum.__class__, set())
    if datum.value not in black_list:
      self._index[datum.GetFullName()] = datum

  def Items(self):
    """Access data from EventData.

    Yields:
      EventDatum: event datum.
    """
    for datum in self._index:
      yield self._index[datum]

  def Get(self, reference_datum, default=None):
    """Access datum with FullName() same as reference_datum.

    Args:
      reference_datum (EventDatum): reference_datum.GetFullName() determines
          datum name to be returned.
      default (object): if no datum is found.

    Returns:
      EventDatum: datum from EventData with FullName specified by
          reference_datum.
    """
    if reference_datum.GetFullName() in self._index:
      return self._index[reference_datum.GetFullName()]
    else:
      return default

  def Empty(self):
    """Check if EventData is empty.

    Returns:
      bool: whether the EventData is empty.
    """
    return len(self._index) == 0
