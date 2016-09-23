"""Command line interface for eccemotus. """

from __future__ import print_function
import argparse
import json
import os
import sys
import shutil
import eccemotus.eccemotus as E

def create_graph(generator, args):
  """ Handles creating and saving graph from data generator. """
  graph = E.get_graph(generator, args.verbose)
  serialized = graph.minimal_serialize()

  output_file = open(args.output, 'w')

  if args.javascript:
    print("var graph=", end="", file=output_file)
    json.dump(serialized, output_file)
    print(";", file=output_file)
  else:
    json.dump(serialized, output_file)
  output_file.close()


def e2g(args):
  """ Computes lateral graph from data at elastic-search."""
  client = E.get_client(args.host, args.port)
  generator = E.elastic_data_generator(client, args.indices, args.verbose)
  create_graph(generator, args)


def f2g(args):
  """ Computes lateral graph from data at file."""
  # TODO check for errors (can not open, bad format)

  generator = E.file_data_generator(args.input, True)
  create_graph(generator, args)

def render(args):
  """ creates a directory html visualization of graph. """

  directory = args.output.rstrip('/')
  base = os.path.dirname(os.path.abspath(__file__))
  base = os.path.join(base, 'eccemotus_ui')

  if not os.path.exists(args.output):
    os.makedirs(args.output)

  shutil.copy(args.input, directory + '/graph.js')
  shutil.copy(base + '/templates/dirty_index.html', directory + '/index.html')

  base_static = base + '/static'
  static = directory +'/static'
  if not os.path.exists(static):
    os.makedirs(static)

  shutil.copy(base_static + '/d3/d3.min.js', static + '/d3.min.js')
  shutil.copy(base_static + '/lateral-map.js', static + '/lateral-map.js')

  print("open {0:s}".format(directory + '/index.html'))


if __name__ == u'__main__':
  parser = argparse.ArgumentParser(prog=u'eccemotus')
  subparsers = parser.add_subparsers()

  # elastic-search to graph
  sub_e2g = subparsers.add_parser(u'e2g', help=u'elastic to graph')
  sub_e2g.set_defaults(routine=e2g)

  host_help = u'elastic-search ip adress (127.0.0.1)'
  sub_e2g.add_argument(
      u'--host', action=u'store', default=u'127.0.0.1', help=host_help)
  port_help = u'elastic-search port (9200)'
  sub_e2g.add_argument(
      u'--port', action=u'store', type=int, default=9200, help=port_help)

  javascript_help = u'output javascript code'
  sub_e2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  verbose_help = 'print progress'
  sub_e2g.add_argument(
      u'--verbose', action=u'store_true', help=verbose_help)

  output_help = u'output file name'
  sub_e2g.add_argument(
      u'--output', action=u'store', help=output_help, required=True)

  indices_help = u'elastic-search indices to parse'
  sub_e2g.add_argument(
      u'indices', metavar=u'index', nargs=u'+', help=indices_help)


  sub_f2g = subparsers.add_parser(u'f2g', help=u'file(s) to graph')
  sub_f2g.set_defaults(routine=f2g)

  sub_f2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  sub_f2g.add_argument(
      u'--verbose', action=u'store_true', help=verbose_help)

  input_help = u'input file in json_line format'
  sub_f2g.add_argument(
      u'input', action=u'store', help=input_help)

  sub_f2g.add_argument(
      u'output', action=u'store', help=output_help)

  sub_render = subparsers.add_parser(u'render', help=u'creates html visualization')
  sub_render.set_defaults(routine=render)

  input_help = u'javascript with graph (use --javascript flag with f2g or e2g)'
  sub_render.add_argument(
      u'input', action=u'store', help=input_help)

  sub_render.add_argument(
      u'output', action=u'store', help=u'directory to store visualization')


  parsed_args = parser.parse_args()
  parsed_args.routine(parsed_args)
