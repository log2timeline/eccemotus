# -*- coding: utf-8 -*-
""" Provides basic methods for storing lateral movement logs in property Graph.

For default use-case, call CreateGraph(data).MinimalSerialize().
This returns json representation of property graph. This can be directly send to
javascript visualization.
"""

from __future__ import print_function
from collections import defaultdict
import sys

import eccemotus.lib.parsers as P


class Graph(object):
  """Very light-weight implementation of property graph.

    This implementation is not meant to be a general property graph.
    It is meant for storing information about lateral movement.

    Property graph is a set of nodes and edges, where each edge and each node
    can have any number of key/value properties associated with them.

    In our case, we have a very specific set of properties.
    nodes:
      id: Automatic generated unique id
      type: Type/name of the node
            These correspond to information names in parsers.parsers module
      value: Value that the node has.
    Pair (tuple) (type, value) is also unique identifier of a node.

    edge:
      source: Id of a source node
      target: Id of a target node
      type: Type of an edge
        Usual types are
          has: Machine has an user
          is: Machine is ip_address (this is not necessarily true for the whole
              time)
          access: ssh connection
      events:
        List of event ids and timestamps. Those events are responsible for
        creation of given edge. Events can be found by id in timesketch or
        filtered by timestamps.
    In fact, every edge is a graph represents multiple edges created by multiple
    events. Those events are specified in events property of this node.

    In theory, edges are directed. In practice, only place where it makes a
    difference is visualization.

    This dictionary (not class) based implementation has its meaning. It is
    easily extensible and prone to data integrity errors. It also has direct
    mapping to data, that can be used in javascript (d3) visualization.

    """

  # Edge types.
  EDGE_HAS = "has"
  EDGE_IS = "is"
  EDGE_ACCEESS = "access"

  # Rules describing which pairs of information should create which type of
  # edge.
  RULES = [
      (P.SOURCE_MACHINE_IP, P.SOURCE_MACHINE_NAME, EDGE_IS),
      (P.SOURCE_USER_NAME, P.SOURCE_USER_ID, EDGE_IS),
      (P.TARGET_MACHINE_NAME, P.TARGET_MACHINE_IP, EDGE_IS),
      (P.TARGET_USER_NAME, P.TARGET_USER_ID, EDGE_IS),
      (P.SOURCE_MACHINE_IP, P.SOURCE_USER_NAME, EDGE_HAS),
      (P.SOURCE_MACHINE_IP, P.SOURCE_USER_ID, EDGE_HAS),
      (P.SOURCE_MACHINE_NAME, P.SOURCE_USER_NAME, EDGE_HAS),
      (P.SOURCE_MACHINE_NAME, P.SOURCE_USER_ID, EDGE_HAS),
      (P.TARGET_MACHINE_IP, P.TARGET_USER_NAME, EDGE_HAS),
      (P.TARGET_MACHINE_IP, P.TARGET_USER_ID, EDGE_HAS),
      (P.TARGET_MACHINE_NAME, P.TARGET_USER_NAME, EDGE_HAS),
      (P.TARGET_MACHINE_NAME, P.TARGET_USER_ID, EDGE_HAS),
  ]

  def __init__(self):
    """Initialize empty graph."""
    self.edges = []
    self.edges_ids = defaultdict(int)  # Provides fast index for edges
    self.nodes = []
    self.nodes_ids = defaultdict(int)  # Provides fast index for nodes

  def GetAddNode(self, node_type, node_value):
    """Return node's id or create a new one if it does not exist.

      Args:
        node_type (str): type of node derived from information names at
            parser.py
        node_value (str): value of the node.
      Returns:
        int: identifier of node. This is a position of node in self.nodes.

    """

    node = (node_type, node_value)
    if node not in self.nodes_ids:
      self.nodes_ids[node] = len(self.nodes_ids)
      self.nodes.append({
          "id": self.nodes_ids[node],
          "value": node_value,
          "type": node_type
      })

    return self.nodes_ids[node]

  def AddEdge(
      self, source_id, target_id, edge_type, timestamp=None, event_id=None):
    """Add new edge to graph or just add new event to existing edge.

    Args:
      edge_type (str):
      event_id (int|str): identifier for event responsible for this edge.
      source_id (int): id of source node.
      target_id (int): id of target node.
      timestamp (int): timestamp when event happened.
    Returns:
      None
    """

    edge = (source_id, target_id, edge_type)
    if edge in self.edges_ids:
      edge_id = self.edges_ids[edge]
      self.edges[edge_id]["events"].append({"id": event_id,
                                            "timestamp": timestamp})

    else:
      edge_id = len(self.edges)
      self.edges_ids[edge] = edge_id
      self.edges.append({
          "source": source_id,
          "target": target_id,
          "type": edge_type,
          "events": [({"id": event_id,
                       "timestamp": timestamp})],
      })

  def GetSshSource(self, event):
    """ Return most specific ssh_source.

    Knowing that the ssh was from user Dean is better than knowing only the ip
    address.
    Note that user name and user id is extended by machine identifier.

    Args:
      event (dict[str, str]): event information values indexed by their
          information names.

    Returns:
      tuple: containing:
        str|None: type of most specific source. None if no source is present.
        str|None: value of most specific source. None if no source is present.
    """

    # List of things that should be used as ssh source in decreasing priority.
    SSH_SOURCE = [P.SOURCE_USER_NAME, P.SOURCE_USER_ID, P.SOURCE_MACHINE_NAME,
                  P.SOURCE_MACHINE_IP, P.SOURCE_PLASO]
    for key in SSH_SOURCE:
      if key in event:
        return key, event[key]
    return None, None

  def GetSshTarget(self, event):
    """ Return best most specific ssh_target.

    Knowing that the ssh was to user Dean is better than knowing only the ip
    address.
    Note that user name and user id is extended by machine identifier.

    Args:
      event (dict[str, str]): event information values indexed by their
          information names.

    Returns:
      tuple: containing:
        str|None: type of most specific target. None if no target is present.
        str|None: value of most specific target. None if no target is present.
    """

    # List of things that should be used as ssh target in decreasing priority.
    SSH_TARGET = [P.TARGET_USER_NAME, P.TARGET_USER_ID, P.TARGET_MACHINE_NAME,
                  P.TARGET_MACHINE_IP, P.TARGET_PLASO]
    for key in SSH_TARGET:
      if key in event:
        return key, event[key]
    return None, None

  def AddData(
      self, source_type, source_value, target_type, target_value, edge_type,
      event_time, event_id):
    """Add edge with corresponding nodes to graph.

    Args:
      edge_type (str): edge type.
      event_id (int|str): event identifier.
      event_time (str): timestamp for event.
      source_type (str): type of source node.
      source_value (str): value of source node.
      target_type (str): type of target node.
      target_value (str): value of target node.

    Returns:
      None
    """

    source_id = self.GetAddNode(P.get_type(source_type), source_value)
    target_id = self.GetAddNode(P.get_type(target_type), target_value)
    self.AddEdge(source_id, target_id, edge_type, event_time, event_id)

  def AddEvent(self, event):
    """ Processes one parsed event and encodes it to edges and nodes.

    Encoding is based on simple rules. (source, target, edge_type). source and
    target are almost (prefix "source:"/"target:" must be removed) types of new
    nodes. They are also keys to event dictionary which provides value for
    a given node.

    Args:
      event (dict[str, str]): parsed event. Result of ParserManager.parse()
          from parsers.py.

    Returns:
      None

    """

    #Simple rules for ownership and identity
    for rule in self.__class__.RULES:
      # Removing target:/source: prefix
      source_value = event.get(rule[0])

      target_value = event.get(rule[1])
      if not (source_value and target_value):
        continue

      self.AddData(rule[0], source_value, rule[1], target_value, rule[2],
                    event[P.TIMESTAMP], event[P.EVENT_ID])

    #Rules for access edge

    ssh_source_type, ssh_source_value = self.GetSshSource(event)
    ssh_target_type, ssh_target_value = self.GetSshTarget(event)
    if ssh_source_value and ssh_target_value:
      self.AddData(ssh_source_type, ssh_source_value, ssh_target_type,
                    ssh_target_value, self.__class__.EDGE_ACCEESS,
                    event[P.TIMESTAMP], event[P.EVENT_ID])

  def MinimalSerialize(self):
    """Serialized only required information for visualization."""
    return {"nodes": self.nodes, "links": self.edges}


def CreateGraph(data, verbose=False):
  """Creates graph from data.

  Args:
    data (iterable): parsed plaso events. data can be any iterable (list),
        preferably generator, because of memory optimization.

  Returns:
    Graph: property graph for events.

  """
  graph = Graph()
  VERBOSE_INTERVAL = 1000
  for i, event in enumerate(data):
    graph.AddEvent(event)
    if not i % VERBOSE_INTERVAL and verbose:
      print(
          "Nodes:%d Edges: %d" % (len(graph.nodes), len(graph.edges)),
          file=sys.stderr)

  return graph


