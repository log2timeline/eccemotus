# -*- coding: utf-8 -*-
"""Helpful constants and functions for parsers."""

# Canonical names for interesting information (fields).
EVENT_ID = u'event_id'
TIMESTAMP = u'timestamp'

SOURCE_MACHINE_IP = u'source:ip'
SOURCE_MACHINE_NAME = u'source:machine_name'
SOURCE_PLASO = u'source:plaso'
SOURCE_USER_ID = u'source:user_id'
SOURCE_USER_NAME = u'source:user_name'

TARGET_MACHINE_IP = u'target:ip'
TARGET_MACHINE_NAME = u'target:machine_name'
TARGET_PLASO = u'target:plaso'
TARGET_USER_ID = u'target:user_id'
TARGET_USER_NAME = u'target:user_name'

# Black lists for common invalid or uninteresting field values.
BASIC_BLACK_LIST = {
    u'ip': [u'127.0.0.1', u'localhost', u'-', u'::1'],
    u'machine_name': [u'127.0.0.1', u'localhost', u'-'],
    u'user_name': [u'N/A', u'-'],
}
BLACK_LIST = {}
for prefix in [u'source', u'target']:
  for sufix in BASIC_BLACK_LIST.keys():
    BLACK_LIST[prefix + u':' + sufix] = BASIC_BLACK_LIST[sufix]

# Set of handy helper functions.
def GetNodeTypeFromInformation(information):
  """Return type of information.

  Args:
      information (string): canonical name of interesting field.

  Returns:
    str: part of information string after ":".
  """
  return information.split(u':')[1]


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
    # This is needed if data some from elasticsearch. Because it likes to cast
    # things to strings.
    spec = eval(spec)  # pylint: disable=eval-used

  while u'parent' in spec:
    spec = spec[u'parent']
  location = spec.get(u'location', u'')
  t_location = u'/'.join(location.split(u'/')[::-1])
  return t_location
