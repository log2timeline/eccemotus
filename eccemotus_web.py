# -*- coding: utf-8 -*-
"""Runs web server interface for eccemotus."""

import argparse
from eccemotus_ui import lateral

if __name__ == u'__main__':
  parser = argparse.ArgumentParser()

  host_help = u'Host address for flask app (127.0.0.1).'
  parser.add_argument(
      u'--host', action=u'store', default=u'127.0.0.1', help=host_help)

  port_help = u'Port for flask app (5012).'
  parser.add_argument(
      u'--port', action=u'store', type=int, default=5012, help=port_help)

  db_help = u'Sqlite database for storing graphs (eccemotus.sql).'
  parser.add_argument(
      u'--database', action=u'store', default=u'eccemotus.sql', help=db_help)

  args = parser.parse_args()
  lateral.Run(args.host, args.port, args.database)
