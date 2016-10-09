# -*- coding: utf-8 -*-
"""Contains classes for handling data parsed from events."""

class EventDatum(object):
  """Interface for event data of various types/names.

  Datum has a value, a flag whether it describes source or a target of given
  event and a name. Name of the datums is based on it's class name and it's
  string representations is in NAME class constant. Full name of the datum
  describes the exact information the datum stores. It is the datum's name
  expanded by whether it is a source or a target.

  Attributes:
    source (bool): whether the datum describes source.
    target (bool): whether the datum describes target.
    value (str): datum's value.
  """
  # Datum's name. This should be set by each subclass.
  NAME = u''

  def __init__(self, value=None, source=False, target=False):
    """Initializes EventDatum.

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
    """Gets representation of full datum's name.

    Return:
      tuple containing:
        bool: whether the datum describes source.
        bool: whether the datum describes target.
        str: datum's name.
    """
    return (self.source, self.target, self.NAME)

  def __str__(self):
    """Returns readable, printable, string representation of datum.

    Mostly used for debugging purposes.

    Return:
      str: string representation of datum.
    """
    return (self.source, self.target, self.NAME, self.value).__repr__()

class Ip(EventDatum):
  """Class to hold data about ip address."""
  NAME = u'ip'

class MachineName(EventDatum):
  """Class to hold data about machine name."""
  NAME = u'machine_name'

class StorageFileName(EventDatum):
  """Class to hold data about plaso file name."""
  NAME = u'plaso'

class UserId(EventDatum):
  """Class to hold data about user id."""
  NAME = u'user_id'

class UserName(EventDatum):
  """Class to hold data about user name."""
  NAME = u'user_name'

class EventData(object):
  """Collection of EventDatum used to manage data extracted from events.

  Data are indexed by their FullName so for each FullName there can be only one
  datum.

  Attributes:
    event_data_type: data_type of event responsible for creation of this
        EventData.
    event_id (int): id of event responsible for creation of this EventData.
    timestamp (int): timestamp id of event responsible for creation of this
        EventData.
  """
  # Black lists for common invalid or uninteresting datum types and values.
  BLACK_LIST = {
      Ip: set([u'127.0.0.1', u'localhost', u'-', u'::1']),
      MachineName: set([u'127.0.0.1', u'localhost', u'-']),
      UserName: set([u'N/A', u'-']),
  }

  def __init__(
      self, data=None, event_data_type=None, event_id=None, timestamp=None):
    """Initializes empty EventData.

    Args:
      data (iterable[EventDatum]): initial data for this collection.
      event_data_type (str): plaso event data_type.
      event_id (int|str): event identifier.
      timestamp (int): timestamp of event.
    """
    if data is None:
      data = []
    self._index = {}  # Holds each added datum.
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
    if datum.value and datum.value not in black_list:
      self._index[datum.GetFullName()] = datum

  def Items(self):
    """Returns data from EventData.

    Yields:
      EventDatum: event datum.
    """
    for datum in self._index:
      yield self._index[datum]

  def Get(self, reference_datum, default=None):
    """Gets datum with FullName() same as reference_datum.

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

  def IsEmpty(self):
    """Checks if EventData is empty.

    Returns:
      bool: whether the EventData is empty.
    """
    return len(self._index) == 0
