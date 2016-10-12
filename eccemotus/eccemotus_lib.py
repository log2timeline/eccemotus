# -*- coding: utf-8 -*-
"""Front-end for working with lateral graph.

This can be used as a command line tool and as a library as well.
First step is to create a data generator (FileDataGenerator or
ElasticDataGenerator), depending of where you want to get plaso events from.

FileDataGenerator:
  Reads JSON_line file and yield one event at a time. It has to read the whole
  file, but has smaller memory requirements.

ElasticDataGenerator:
  Queries elasticsearch for events that it can parse. It has small memory
  requirements and does not need to read all logs, however must wait for
  elasticsearch.

Then you have to parse the data with ParsedDataGenerator(data_generator).

Last thing you want to do is to call GetGraphJSON(ParsedDataGenerator) to
create the actual graph.
"""

import json
import logging

try:
  from elasticsearch import Elasticsearch
  from elasticsearch import helpers
except ImportError:
  Elasticsearch = None

from lib import graph as graph_lib# pylint: disable=relative-import
from lib.parsers import manager # pylint: disable=relative-import

def FileDataGenerator(filename, verbose=False):
  """Reads JSON_line file and yields events.

  JSON_line file means, that every event is a JSON on a separate line.

  Args:
    filename (str): name of file with events in JSON_line format.

  Yields:
    dict: event.
  """
  logger = logging.getLogger(__name__)
  with open(filename, u'r') as input_file:
    for i, line in enumerate(input_file):
      if not i % 100000 and verbose:
        logger.info(u'File line {0:d}'.format(i))
      yield json.loads(line)


def ElasticDataGenerator(client, indexes, query=None, verbose=False):
  """Reads event data from elasticsearch.

  Uses scan function, so the data are actually streamed and do not need to be
  in RAM.

  Args:
    client (Elasticsearch): elasticsearch client.
    indexes (list[str]): elasticsearch indexes.
    query (None|dict): if specified, query is used as elasticsearch query.
    verbose (bool): control for verbosity.

  Yields:
    dict: JSON representation of plaso event.

  Raises:
    ImportError: when you do not have elasticsearch installed.
  """
  if Elasticsearch is None:
    raise ImportError((u'Please install elasticsearch to use this'
                       u'functionality.'))

  # Term filter for data_types, that we can parse.
  should = [{u'term': {u'data_type': data_type}}
            for data_type in manager.ParserManager.GetParsedTypes()]
  if not query:
    query = {u'match_all': {}}

  # Elasticsearch query.
  full_query = {
      u'query': {
          u'filtered': {
              u'query': query,
              u'filter': {
                  u'bool': {
                      u'should': should,
                  }
              }
          }
      }
  }
  VERBOSE_INTERVAL = 10000
  logger = logging.getLogger(__name__)
  results = helpers.scan(client, query=full_query, index=indexes)
  for i, response in enumerate(results):
    if not i % VERBOSE_INTERVAL and verbose:
      logger.info(u'Elastic records {0:d}'.format(i))

    event = response['_source']
    event[u'timesketch_id'] = response[u'_id']
    yield event


def GetClient(host, port):
  """Creates elasticsearch client.

  Args:
    host (str): ip address.
    port (int): port number.

  Returns:
    Elasticsearch: elasticsearch client.

  Raises:
    ImportError: when you do not have elasticsearch installed.
  """
  if Elasticsearch is None:
    raise ImportError((u'Please install elasticsearch to use this '
                       u'functionality.'))

  client = Elasticsearch([{u'host': host, u'port': port}])
  return client


def ParsedDataGenerator(raw_generator):
  """Transforms raw event generator to parsed event generator.

  Args:
    raw_generator (iterable[dict]): Plaso events.

  Yields:
    dict: parsed Plaso events.
  """
  for raw_event in raw_generator:
    if not raw_event:
      continue
    parsed = manager.ParserManager.Parse(raw_event)
    if parsed:
      yield parsed


def GetGraph(raw_generator, verbose=False):
  """Creates graph from raw data.
  Args:
    raw_generator (iterable[dict]): plaso events

  Returns:
    Graph: graph created based on events.
  """
  parsed_generator = ParsedDataGenerator(raw_generator)
  graph = graph_lib.CreateGraph(parsed_generator, verbose)
  return graph
