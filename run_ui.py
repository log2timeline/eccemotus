"""Runs web server interface for eccemotus. """
import argparse
from eccemotus_ui.lateral import run

if __name__ == u'__main__':
  parser = argparse.ArgumentParser()

  host_help = u'host address for flask app (default 127.0.0.1)'
  parser.add_argument(
      u'--host', action=u'store', default=u'127.0.0.1', help=host_help)

  port_help = u'port for flask app (default 5012)'
  parser.add_argument(
      u'--port', action=u'store', type=int, default=5012, help=port_help)

  db_help = (
      u'sqlite database you want to use for storing graphs '
      u'(default eccemotus.sql)')
  parser.add_argument(
      u'--database', action=u'store', default=u'eccemotus.sql', help=db_help)

  args = parser.parse_args()
  run(args.host, args.port, args.database)
