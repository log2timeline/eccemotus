# -*- coding: utf-8 -*-
"""Command line interface for eccemotus."""

from __future__ import print_function
import argparse
import json
import os
import shutil
from  eccemotus import eccemotus_lib as eccemotus  # pylint: disable=no-name-in-module


def CreateGraph(generator, args):
  """Handles creating and saving graph from data generator.

  Args:
    generator (iterable[dict]): plaso events, usually
        eccemotus.FileDataGenerator or eccemotus.ElasticDataGenerator.
    args (argparse.Namespace): command line arguments.
  """
  graph = eccemotus.GetGraph(generator, args.verbose)
  serialized = graph.MinimalSerialize()

  with open(args.output, u'w') as output_file:
    if args.javascript:
      print(u'var graph=', end='', file=output_file)
      json.dump(serialized, output_file)
      print(u';', file=output_file)
    else:
      json.dump(serialized, output_file)


def ElasticToGraph(args):
  """Computes lateral graph based on data from elastic-search.

  Args:
    args (argparse.Namespace): command line arguments.
  """
  client = eccemotus.GetClient(args.host, args.port)
  generator = eccemotus.ElasticDataGenerator(client, args.indices, args.verbose)
  CreateGraph(generator, args)


def FileToGraph(args):
  """Computes lateral graph based on data from file.

  Args:
    args (argparse.Namespace): command line arguments.
  """
  generator = eccemotus.FileDataGenerator(args.input, args.verbose)
  CreateGraph(generator, args)


def Render(args):
  """Creates a directory with a html visualization of graph.

  Args:
    args (argparse.Namespace): command line arguments.
  """
  directory = args.output
  # We use this dirty trick to infer the directory where eccemotus_ui is
  # installed because we need to copy some files from that directory.
  from eccemotus_ui import lateral
  base = os.path.dirname(lateral.__file__)
  if not os.path.exists(args.output):
    os.makedirs(args.output)

  shutil.copy(args.input, os.path.join(directory, u'graph.js'))
  index_path = os.path.join(base, u'templates/dirty_index.html')
  index_new_path = os.path.join(directory, u'index.html')

  shutil.copy(index_path, index_new_path)

  base_static = os.path.join(base, u'static')
  static = os.path.join(directory, u'static')
  if not os.path.exists(static):
    os.makedirs(static)

  shutil.copy(
      os.path.join(base_static, u'd3/d3.min.js'),
      os.path.join(static, u'd3.min.js'))
  shutil.copy(
      os.path.join(base_static, u'lateral-map.js'),
      os.path.join(static, u'lateral-map.js'))

  print(u'open {0:s}'.format(os.path.join(directory, u'index.html')))


if __name__ == u'__main__':
  parser = argparse.ArgumentParser(prog=u'eccemotus')
  subparsers = parser.add_subparsers()

  # elastic-search to graph
  sub_e2g_help = (
      u'Retrieve events from elasticsearch database and create a graph based '
      u'on them.')
  sub_e2g = subparsers.add_parser(u'e2g', help=sub_e2g_help)
  sub_e2g.set_defaults(routine=ElasticToGraph)

  host_help = u'Elastic-search ip adress (127.0.0.1).'
  sub_e2g.add_argument(
      u'--host', action=u'store', default=u'127.0.0.1', help=host_help)
  port_help = u'Elastic-search port (9200).'
  sub_e2g.add_argument(
      u'--port', action=u'store', type=int, default=9200, help=port_help)

  javascript_help = u'Output javascript code instead of JSON. Used in render.'

  sub_e2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  verbose_help = u'Print progress.'
  sub_e2g.add_argument(u'--verbose', action=u'store_true', help=verbose_help)

  output_help = u'Output file name.'
  sub_e2g.add_argument(
      u'--output', action=u'store', help=output_help, required=True)

  indices_help = u'Elastic-search indices to parse.'
  sub_e2g.add_argument(
      u'indices', metavar=u'index', nargs=u'+', help=indices_help)

  sub_f2g_help = (
      u'Retrieve events from json_line file and create a graph based on them.')
  sub_f2g = subparsers.add_parser(u'f2g', help=sub_f2g_help)
  sub_f2g.set_defaults(routine=FileToGraph)

  sub_f2g.add_argument(
      u'--javascript', action=u'store_true', help=javascript_help)

  sub_f2g.add_argument(u'--verbose', action=u'store_true', help=verbose_help)

  input_help = u'Input file in json_line format. See plaso json_line.'
  sub_f2g.add_argument(u'input', action=u'store', help=input_help)

  sub_f2g.add_argument(u'output', action=u'store', help=output_help)

  render_help = u'Creates html visualization.'
  sub_render = subparsers.add_parser(u'render', help=render_help)
  sub_render.set_defaults(routine=Render)

  input_help = u'Javascript with graph (use --javascript flag with f2g or e2g).'
  sub_render.add_argument(u'input', action=u'store', help=input_help)

  render_help = u'Directory to store the visualization and required files.'
  sub_render.add_argument(u'output', action=u'store', help=render_help)

  parsed_args = parser.parse_args()
  parsed_args.routine(parsed_args)
