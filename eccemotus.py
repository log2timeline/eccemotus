# -*- coding: utf-8 -*-
"""Command line interface for eccemotus. """

from __future__ import print_function
import argparse
import json
import os
import shutil
import eccemotus.eccemotus as E  # pylint: disable=no-name-in-module


def CreateGraph(generator, args):
  """Handles creating and saving graph from data generator."""
  graph = E.GetGraph(generator, args.verbose)
  serialized = graph.MinimalSerialize()

  with open(args.output, u'w') as output_file:
    if args.javascript:
      print(u'var graph=', end='', file=output_file)
      json.dump(serialized, output_file)
      print(u';', file=output_file)
    else:
      json.dump(serialized, output_file)


def ElasticToGraph(args):
  """Computes lateral graph from data at elastic-search."""
  client = E.GetClient(args.host, args.port)
  generator = E.ElasticDataGenerator(client, args.indices, args.verbose)
  CreateGraph(generator, args)


def FileToGraph(args):
  """Computes lateral graph from data at file."""
  generator = E.FileDataGenerator(args.input, True)
  CreateGraph(generator, args)


def Render(args):
  """Creates a directory html visualization of graph."""

  directory = args.output.rstrip(u'/')
  base = os.path.dirname(os.path.abspath(__file__))
  base = os.path.join(base, u'eccemotus_ui')

  if not os.path.exists(args.output):
    os.makedirs(args.output)

  shutil.copy(args.input, directory + u'/graph.js')
  shutil.copy(base + u'/templates/dirty_index.html', directory + u'/index.html')

  base_static = base + u'/static'
  static = directory +u'/static'
  if not os.path.exists(static):
    os.makedirs(static)

  shutil.copy(base_static + u'/d3/d3.min.js', static + u'/d3.min.js')
  shutil.copy(base_static + u'/lateral-map.js', static + u'/lateral-map.js')

  print(u'open {0:s}'.format(directory + u'/index.html'))


if __name__ == u'__main__':
  parser = argparse.ArgumentParser(prog=u'eccemotus')
  subparsers = parser.add_subparsers()

  # elastic-search to graph
  sub_e2g = subparsers.add_parser(u'e2g', help=u'elastic to graph')
  sub_e2g.set_defaults(routine=ElasticToGraph)

  host_help = u'elastic-search ip adress (127.0.0.1)'
  sub_e2g.add_argument(
      u'--host', action=u'store', default=u'127.0.0.1', help=host_help)
  port_help = u'elastic-search port (9200)'
  sub_e2g.add_argument(
      u'--port', action=u'store', type=int, default=9200, help=port_help)

  javascript_help = u'output javascript code'
  sub_e2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  verbose_help = u'print progress'
  sub_e2g.add_argument(u'--verbose', action=u'store_true', help=verbose_help)

  output_help = u'output file name'
  sub_e2g.add_argument(
      u'--output', action=u'store', help=output_help, required=True)

  indices_help = u'elastic-search indices to parse'
  sub_e2g.add_argument(
      u'indices', metavar=u'index', nargs=u'+', help=indices_help)


  sub_f2g = subparsers.add_parser(u'f2g', help=u'file(s) to graph')
  sub_f2g.set_defaults(routine=FileToGraph)

  sub_f2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  sub_f2g.add_argument(u'--verbose', action=u'store_true', help=verbose_help)

  input_help = u'input file in json_line format'
  sub_f2g.add_argument(u'input', action=u'store', help=input_help)

  sub_f2g.add_argument(u'output', action=u'store', help=output_help)

  render_help = u'creates html visualization'
  sub_render = subparsers.add_parser(u'render', help=render_help)
  sub_render.set_defaults(routine=Render)

  input_help = u'javascript with graph (use --javascript flag with f2g or e2g)'
  sub_render.add_argument(u'input', action=u'store', help=input_help)

  render_help = u'directory to store visualization'
  sub_render.add_argument(u'output', action=u'store', help=render_help)


  parsed_args = parser.parse_args()
  parsed_args.routine(parsed_args)
