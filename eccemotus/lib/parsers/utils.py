# -*- coding: utf-8 -*-
"""Contains useful functions for parsers."""

def FirstValidDatum(data, default=None):
  """Return

  Args:
    data (list[event_data.EventDatum]): list of event data.
    default (object): returned in case no no valid datum was found.
  """
  for datum in data:
    if not datum:
      continue
    if datum.value:
      return datum.value
  return default


def FirstTrue(values, default=None):
  """Return first True (not None, not empty...) value or default.

  Args:
    values (iterable): list of values to choose from.
    default (optional): default return.

  Returns:
    ?: first True object.
  Used to determine a meaningful name for a machine.
  """
  for value in values:
    if value:
      return value
  return default


def GetImageName(event):
  """Returns path to plaso file that the log came from.

  Actual directories in actual path are in reversed order.
  Example: /tmp/work/dump.plaso ---> dump.plaso/work/tmp/
  The path is more readable in visualization (because of trimming long names).

  Args:
    event (dict): json serialized plaso event.

  Returns:
    str: path to plaso file in reversed order (look down at the example).
  """
  spec = event.get(u'pathspec', {})
  if isinstance(spec, basestring):
    # This is needed in case data come from elasticsearch. event['pathspec']
    # is naturally a nested dictionary but elastic search returns it as a
    # string.
    spec = eval(spec)  # pylint: disable=eval-used

  while u'parent' in spec:
    spec = spec[u'parent']
  location = spec.get(u'location', u'')
  t_location = u'/'.join(location.split(u'/')[::-1])
  return t_location
