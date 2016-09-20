"""Front-end for working with lateral graph.

This can be used as a command line tool and as a library as well.
First step is to create a data generator (file_data_generator or
elastic_data_generator), depending of where you want to get plaso events from.

file_data_generator:
  Reads json_line file and yield one event at a time. It has to read the whole
  file, but has no memory requirements.

elastic_data_generator:
  Queries elasticsearch for events that it can parse. Also no memory
  requirements. Does not need to read all logs, but must wait for elasticsearch.

Than you have to parse the data with parsed_data_generator(data_generator).

Last think you want to do is to call get_graph_json(parsed_data_generator)
to create the actual graph.
"""

from __future__ import print_function
import sys
import json
from eccemotus.lib.grapher import create_graph
from eccemotus.lib.parsers import ParserManager


def file_data_generator(filename, verbose=False):
  """Reads json_line file and yields events.

    Json_line means, that every event is a json on a separate line.
    """
  input_file = open(filename)
  for i, line in enumerate(input_file):
    if not i % 100000 and verbose:
      print("File line ", i, file=sys.stderr)
    yield json.loads(line)


def elastic_data_generator(client, indexes, verbose=False):
  """Reads event data from elasticsearch.

    Args:
        client: Elasticsearch client.
        indexes: List of elasticsearch indexes.
        verbose: If True, prints progress.

    Yield:
        plaso event.


    Uses scan function, so the data is really processed like a stream.
    """
  from elasticsearch.helpers import scan  #TODO add try except

  # Generating term filter for data_types, that we can parse
  should = [{"term": {"data_type": data_type}}
            for data_type in ParserManager.get_parsed_types()]

  # Elasticsearch query.
  query = {
      "query": {
          "filtered": {
              "query": {"match_all": {}},
              "filter": {
                  "bool": {
                      "should": should,
                  }
              }
          }
      }
  }

  # this is a bug at elasticsearch.py, because it can not handle elastic errors
  # properly. it is sad :'(
  try:  #TODO(vlejd) fix this.
    for i, response in enumerate(scan(client, query=query, index=indexes)):
      if not i % 10000 and verbose:
        print("Elastic records ", i, file=sys.stderr)

      event = response['_source']
      event["timesketch_id"] = response["_id"]
      yield event
  except Exception as e:

    return


def get_client(host, port):
  """ Returns elasticsearch client for given port and host address."""
  from elasticsearch import Elasticsearch  #TODO add try except
  client = Elasticsearch([{u'host': host, u'port': port}])
  return client


def parsed_data_generator(raw_generator):
  """Transform raw event generator to parsed events generator."""
  for raw_event in raw_generator:
    if not raw_event:
      continue
    parsed = ParserManager.parse(raw_event)
    if parsed:
      yield parsed


def get_graph(raw_generator, verbose=False):
  parsed_generator = parsed_data_generator(raw_generator)
  graph = create_graph(parsed_generator, verbose)
  return graph


def get_graph_json(raw_generator, verbose=False):
  """Returns json representation for graph created based on raw_generator."""

  graph = get_graph(raw_generator, verbose=verbose)
  graph_json = json.dumps(graph.minimal_serialize())
  return graph_json


def get_one(client, idd, indexes):
  from elasticsearch.helpers import scan  #TODO add try except
  for ind in indexes:
    try:
      res = client.get(index=ind, id=idd)
      print(ParserManager.parse(res['_source']))
    except:
      print("nope")

#TODO this will have its own command line interface.