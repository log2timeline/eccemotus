# -*- coding: utf-8 -*-

__version__ = '0.0.1'

VERSION_DEV = True
VERSION_DATE = '20161016'


def GetVersion():
  """Retrieves the version.

  Returns:
    A string containing the version.
  """
  if VERSION_DEV:
    return u'{0:s}_{1:s}'.format(__version__, VERSION_DATE)

  return __version__
